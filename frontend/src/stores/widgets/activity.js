import {types} from 'mobx-state-tree';

import {getActivity} from 'api/routes';

import Widget from './widget';

const ActivityData = types
    .model('ActivityData', {
        likes: types.number,
        reposts: types.number,
        views: types.number,
        comments: types.number,
        posts: types.number,
    });

const ActivityDataSettings = types
    .model('ActivityDataSettings', {
        period: types.string,
    });


const Activity = types
    .model('ActivityWidget', {
        type: 'Activity',
        data: types.maybeNull(ActivityData),
        settings: types.optional(ActivityDataSettings, {
            period: '1d',
        }),
    })
    .actions(() => {
        const loader = async (settings) => {
            return getActivity(settings);
        };

        return {loader};
    });

export default types.compose(
    Widget,
    Activity,
).named('ActivityWidget');
