import {
    dataApi as api,
    jazzApi as jApi,
} from './index';

export const getTopPosts = ({period, count, sortKey}) => {
    return api.get(`api/v1.0/stats/posts/top?period=${period}&count=${count}&sortKey=${sortKey}`)
        .then(({data}) => data);
};

export const getActivity = ({period}) => {
    return api.get(`/api/v1.0/stats/events/activity?period=${period}`)
        .then(({data}) => data);
};


export const auth = () => {
    return Promise.resolve({
        id: '1',
        token: 'token',
    }) || jApi.get('/api/v0.0/auth');
};

export const getSettings = () => {
    return Promise.resolve({
        vk: {
            groupId: '193519310',
            dashboards: [
                'dashboard1',
            ],
        },
    }) || jApi.get('/api/v0.0./settings');
};

export const getDashboard = (id) => {
    return Promise.resolve({
        id: 'dashboard1',
        name: 'Test Dashboard',
        description: 'Description of dashboard',
        widgetSettings: {
            topPosts: {
                minHeight: 4,
                minWidth: 4,
                resizable: true,
            },
        },
        widgets: [
            {
                type: 'topPosts',
                settings: {
                    period: '1w',
                    count: 3,
                    sortKey: 'default',
                    updateEvery: '10m',
                },
                position: {
                    x: 0,
                    y: 0,
                    h: 4,
                    w: 4,
                },
            },
        ],
    }) || jApi.get('/api/v0.0./dashboard');
};
