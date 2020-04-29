import api from './index';

export const getTopPosts = (duration) => {    
    return api.get(`/stats/posts/top?duration=${duration}`).then(({data}) => {
        return data
    });
}