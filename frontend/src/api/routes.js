import api from './index';

export const getTopPosts = (duration) => {    
    return api.get(`/stats/posts/top?duration=${duration}`).then(({data}) => {
        return {
            id: data.id,
            comments: data.comments_count,
            reposts: data.reposts_count,
            likes: data.likes_count,
            view: data.view_count,
        }
    });
}