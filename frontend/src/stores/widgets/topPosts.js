import {types} from 'mobx-state-tree';

import {getTopPosts} from 'api/routes';

import Widget from './widget';

const TopPostItem = types
    .model('TopPostItem', {
        likesCount: types.number,
        vkId: types.number,
        repostsCount: types.number,
        viewsCount: types.number,
        commentsCount: types.number,
    });

const TopPostSettings = types
    .model('TopPostSettings', {
        period: types.string,
        count: types.number,
        sortKey: types.string,
    });


const TopPosts = types
    .model('TopPostsWidget', {
        type: 'TopPosts',
        data: types.array(TopPostItem, []),
        settings: types.optional(TopPostSettings, {
            period: '1d',
            count: 3,
            sortKey: 'default',
        }),
    })
    .actions(() => {
        const loader = async (settings) => {
            return getTopPosts(settings);
        };

        return {loader};
    });

export default types.compose(
    Widget,
    TopPosts,
).named('TopPostsWidget');
