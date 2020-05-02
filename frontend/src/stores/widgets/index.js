import {types} from 'mobx-state-tree';

import Widget from './widget';

import TopPosts from './topPosts';
import Activity from './activity';

const map = {
    topPosts: TopPosts,
    activity: Activity,
};

const Widgets = types
    .model('Widgets', {
        widgets: types.map(Widget),
    })
    .actions((self) => {
        const widgets = self;

        const getWidget = (type) => {
            return widgets[type];
        };

        const setWidget = (widget) => {
            widgets[widget.type] = map[widget.type].create(widget);
        };

        return {getWidget, setWidget};
    });

export default Widgets;
