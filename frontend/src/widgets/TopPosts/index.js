import React from 'react';

import Spin from 'components/Spin';
import ActivityMonitor from 'components/ActivityCounter';
import WidgetHeader from 'components/WidgetHeader';

import {connectToWidget} from 'tools/connect';

import './style.scss';

function TopPosts({isLoading, error, data}) {
    return (
        <div className="TopPosts">
            {isLoading ? <Spin /> : (
                <React.Fragment>
                    <WidgetHeader title="Top 3 posts" onSetup={() => {}} />
                    {error ? <h1>Ощибка</h1> : data.map((e) => {
                        return (
                            <div className="TopPosts__post">
                                <a href={`https://vk.com/public193519310?w=wall-193519310_${e.vk_id}`}>Post ID: {e.id}</a>
                                <ActivityMonitor {...e} />
                            </div>
                        );
                    })}
                </React.Fragment>
            )}
        </div>
    );
}

export default connectToWidget('topPosts')(TopPosts);
