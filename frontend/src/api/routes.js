import api from './index';

export const getTopPosts = ({period, count, sortKey}) => {
    return api.get(`api/v1.0/stats/posts/top?period=${period}&count=${count}&sortKey=${sortKey}`)
        .then(({data}) => data);
};

export const getActivity = ({period}) => {
    return api.get(`/api/v1.0/stats/events/activity?period=${period}`)
        .then(({data}) => data);
};
