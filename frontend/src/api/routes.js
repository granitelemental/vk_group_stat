import api from './index';

export const getTopPosts = (period) => {    
    return api.get(`api/v1.0/stats/posts/top?period=${period}`).then(({data}) => data);
}