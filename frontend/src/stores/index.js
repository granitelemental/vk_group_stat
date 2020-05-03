import {types} from 'mobx-state-tree';
// import auth from './auth';

import Widgets from './widgets';

const Store = types
    .model('Store', {
        // auth: types.optional(auth, {}),
        widgets: types.optional(Widgets, {}),
    })
    .actions((self) => {
        const store = self;

        // const reset = () => {
        //     applySnapshot(store.wizard, {});
        //     applySnapshot(store.pages, {});
        //     applySnapshot(store.quickSearch, {});
        // };

        const afterCreate = () => {
            store.widgets.setWidget({
                type: 'topPosts',
            });

            store.widgets.setWidget({
                type: 'activity',
            });
        };

        return {afterCreate};
    });

export default Store;
