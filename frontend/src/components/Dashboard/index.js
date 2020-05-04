import React from 'react';
import RGL, {WidthProvider} from 'react-grid-layout';

import './style.scss';

const ReactGridLayout = WidthProvider(RGL);

export default class Dashboard extends React.PureComponent {
    onLayoutChange = (layout) => {
        this.props.onLayoutChange(layout);
    }

    onResize(layout, oldLayoutItem, layoutItem, placeholder) {
        // `oldLayoutItem` contains the state of the item before the resize.
        // You can modify `layoutItem` to enforce constraints.

        if (layoutItem.h < 3 && layoutItem.w > 2) {
            layoutItem.w = 2;
            placeholder.w = 2;
        }

        if (layoutItem.h >= 3 && layoutItem.w < 2) {
            layoutItem.w = 2;
            placeholder.w = 2;
        }
    }

    render() {
        const {widgets, isEdit} = this.props;
        return (
            <div className="react-grid-layout">
                <ReactGridLayout
                    onLayoutChange={this.onLayoutChange}
                    onResize={this.onResize}
                    isDraggable={isEdit}
                    isResizable={isEdit}
                    items={20}
                    rowHeight={30}
                    cols={6}
                >
                    {widgets.map(({Widget, grid}) => {
                        return (
                            <div key={grid.i} data-grid={grid}>
                                <Widget />
                            </div>
                        );
                    })}
                </ReactGridLayout>
            </div>
        );
    }
}

Dashboard.defaultProps = {
    isDraggable: true,
    isResizable: true,
    items: 20,
    rowHeight: 30,
    onLayoutChange() {},
    cols: 4,
};
