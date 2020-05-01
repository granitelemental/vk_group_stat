import config from 'configs';

import keysToCamel from './keysToCamel';

// import mock from './mock';

const flattenError = (err) => {
    if (Array.isArray(err)) {
        return err.join(', ');
    }
    return Object.values(err).map(flattenError).join('\r\n');
};

export const getApiPath = (path) => {
    return `${config.api}${config.api.endsWith('/') ? '' : '/'}${path.startsWith('/') ? path.slice(1) : path}`;
};
const callApi = (path, options) => {
    const url = getApiPath(path);
    // if (environment === 'test') return mock(url, options);
    return fetch(url, {
        headers: options.headers ? options.headers : {'Content-type': 'application/json; charset=utf-8'},
        ...options,
    })
        .then((res) => {
            if (res.status === 401) {
                throw new Error('Сессия истекла. Авторизуйтесь заново');
            }
            if (res.status === 500 || res.status === 504 || res.status === 502) {
                throw new Error('На сервере произошла ошибка, повторите попытку позже');
            }
            return res;
        })
        .then((res) => {
            switch (options.format) {
                case 'json':
                    return res.json();
                case 'text':
                    return res.text();
                case 'blob':
                    return res.blob();
                case 'formData':
                    return res.formData();
                case 'arrayBuffer':
                    return res.arrayBuffer();
                default:
                    return res.json();
            }
        })
        .then(data => {
            return keysToCamel(data);
        })
        .catch((data) => {
            if (data instanceof TypeError && data.message === 'Failed To Fetch') {
                throw new Error()
            }
            throw data;
        });
};

const api = {
    get: (path, options = {}) => callApi(path, {...options, method: 'GET'}),
    post: (path, options = {}) => callApi(path, {...options, method: 'POST', body: JSON.stringify(options.body || '')}),
    patch: (path, options = {}) => callApi(path, {...options, method: 'PATCH', body: JSON.stringify(options.body || '')}),
    put: (path, options = {}) => callApi(path, {...options, method: 'PUT', body: JSON.stringify(options.body || '')}),
    delete: (path, options = {}) => callApi(path, {...options, method: 'DELETE', body: JSON.stringify(options.body || '')}),
    upload: (path, options = {}) => callApi(path, {...options, method: 'POST', body: options.body, headers: {...(options.headers || {})}}),
};

export default api;
