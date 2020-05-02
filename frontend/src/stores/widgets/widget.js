import {types, flow} from 'mobx-state-tree';

const Widget = types
    .model('Widget', {
        type: types.string,
        error: types.maybeNull(types.string),
        isLoading: types.optional(types.boolean, true),
    })
    .actions((self) => {
        const widget = self;

        const afterCreate = flow(function* ajax() {
            yield widget.load();
        });

        const load = flow(function* ajax() {
            try {
                widget.isLoading = true;
                const data = yield widget.loader(widget.settings);
                widget.data = data;
            } catch (err) {
                widget.error = err.message;
            } finally {
                widget.isLoading = false;
            }
        });

        return {
            load,
            afterCreate,
        };
    });

export default Widget;
