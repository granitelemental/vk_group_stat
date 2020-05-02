import {types, flow, getRoot} from 'mobx-state-tree';
import api from 'api';
import {configureScope} from '@sentry/browser';
import {AUTH_ROUTE, TERMS_ROUTE, CAMPAIGN_ROUTE, DASHBOARD_ROUTE, MONITORING_VIEW, CCT_VIEW} from 'constants/routes';
import history from 'tools/history';

const Auth = types
    .model('Auth', {
        user: types.maybeNull(types.frozen(null)),
        permissions: types.maybeNull(types.frozen(null)),
        isLoading: types.optional(types.boolean, false),
        campaign: types.maybeNull(types.frozen({})),
        terms: types.maybeNull(types.string),
        needsToFillContacts: types.optional(types.boolean, false),
    })
    .actions((self) => {
        const auth = self;
        const {addNotification} = getRoot(self).common;

        const submitLogin = flow(function* ajax(userLogin, userPassword) {
            auth.isLoading = true;
            try {
                yield api.post('api/auth/login', {body: {login: userLogin, password: userPassword}});
                yield auth.getCampaign();
                if (auth.campaign.title) {
                    auth.isLoading = false;
                    history.push(AUTH_ROUTE + CAMPAIGN_ROUTE);
                }
                yield auth.loadUserData();
                yield auth.loadUserPermission();

                if (!auth.user.organizationTermsIsConfirmed && auth.user.orgType === 'partner') {
                    yield auth.getTerms();
                    auth.isLoading = false;
                    return history.push(AUTH_ROUTE + TERMS_ROUTE);
                }
                
                auth.checkNeedsToFillContacts();
                
                if (!auth.isShowAuth) auth.navigateToMainPage();
            } catch (err) {
                addNotification(err || 'Произошла ошибка авторизации');
            }

            auth.isLoading = false;
        });

        const checkNeedsToFillContacts = () => {
            auth.needsToFillContacts = auth.user.orgType === 'partner' && (!auth.user.organizationEmail || !auth.user.organizationAddress || !auth.user.organizationTelephone);
        };

        const resetNeedsToFillContacts = () => auth.needsToFillContacts = false;

        const navigateToMainPage = () => {
            history.push(auth.user.orgType === 'partner' ? DASHBOARD_ROUTE : MONITORING_VIEW + CCT_VIEW);
        };

        const getTerms = flow(function* ajax() {
            try {
                const terms = yield api.get(auth.user.termsUrl, {format: 'text'});
                auth.terms = terms;
            } finally {
                //
            }
        });

        const confirmTerms = flow(function* ajax() {
            auth.isLoading = true;
            try {
                yield api.post('api/auth/confirm_terms');
            } finally {
                auth.terms = null;
                auth.user = {...auth.user, organizationTermsIsConfirmed: true};
            }

            if (auth.campaign.title) {
                history.push(AUTH_ROUTE + CAMPAIGN_ROUTE);
            } else {
                auth.navigateToMainPage();
            }
            auth.isLoading = false;
        });

        const confirmCampaign = flow(function* ajax() {
            auth.isLoading = true;
            try {
                yield api.patch(`api/campaign/mark_read/${auth.campaign.id}`);
            } finally {
                auth.isLoading = false;
                auth.campaign = null;
                auth.navigateToMainPage();
            }
        });

        const afterCreate = flow(function* ajax() {
            yield auth.loadUserData();
            yield auth.loadUserPermission();
            if (localStorage.getItem('authFromOldApp')) {
                localStorage.removeItem('authFromOldApp');
                auth.checkNeedsToFillContacts();
            }
        });

        const loadUserData = flow(function* ajax() {
            try {
                const {data} = yield api.get('api/auth/get_user_info');
                auth.user = data;
                // Sentry user info configuration
                configureScope((scope) => {
                    const {id, name, email, login, orgType} = auth.user;
                    scope.setUser({id, name, email, login, orgType});
                });
            } catch (err) {
                auth.user = {};
            }
        });

        const loadUserPermission = flow(function* ajax() {
            try {
                const {data} = yield api.get(`api/organization/user_group/?user_id=${auth.user.id}`);
                auth.permissions = data;
            } catch (err) {
                auth.permissions = null;
            }
        });

        const logout = flow(function* ajax(makeAjaxLogout = true) {
            // eslint-disable-next-line
            if (getRoot(self).common.historyUnblock && !window.confirm('При выходе из аккаунта несохраненные данные могут быть утеряны, продолжить?')) {
                return;
            }
            getRoot(self).common.showOnBeforeUnload(false);
            
           
            try {
                if (makeAjaxLogout) yield api.post('api/auth/logout');
                auth.user = {};
            } catch (err) {
                auth.user = {};
            }
            history.push(AUTH_ROUTE);
            getRoot(self).reset();
        });

        const getCampaign = flow(function* ajax() {
            try {
                const {data} = yield api.get(`api/campaign/get_one_unread?t=${parseInt(+new Date('2020-01-01') / 1000, 10)}`);
                auth.campaign = data.campaign || {};
            } catch (err) {
                // console.log(err);
            }
        });

        return {
            afterCreate,
            loadUserData,
            loadUserPermission,
            logout,
            getCampaign,
            submitLogin,
            confirmCampaign,
            navigateToMainPage,
            confirmTerms,
            getTerms,
            checkNeedsToFillContacts,
            resetNeedsToFillContacts,
        };
    })
    .views((auth) => ({
        get isShowAuth() {
            if (!auth.user || !auth.user.id) return true;

            const termIsConfirmed = auth.user.organizationTermsIsConfirmed || auth.user.orgType !== 'partner';

            return (auth.campaign && auth.campaign.title) || !termIsConfirmed;
        },
        hasOneOfPermission(permissions) {
            if (!auth.permissions) return false;
            const permissionList = Array.isArray(permissions) ? permissions : [permissions];

            return permissionList.reduce((result, permission) => {
                return result || auth.permissions.perms.some(({name}) => name === permission);
            }, false);
        },
    }));

export default Auth;
