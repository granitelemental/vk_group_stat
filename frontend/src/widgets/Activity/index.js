import React from 'react';

import Spin from 'components/Spin';
import WidgetHeader from 'components/WidgetHeader';

import {connectToWidget} from 'tools/connect';

// import './style.scss';

function Activity({isLoading, error, data}) {
    return (
        <div className="Activity">
            {isLoading ? <Spin /> : (
                <React.Fragment>
                    <WidgetHeader title="Activity" onSetup={() => {}} />
                    {error ? <h1>Ощибка</h1> : (
                        <React.Fragment>
                            <ul className="list-group">
                                <li className="list-group-item">Posts: <b>{data.posts}</b></li>
                                <li className="list-group-item">Likes: <b>{data.likes}</b></li>
                                <li className="list-group-item">Comments: <b>{data.comments}</b></li>
                                <li className="list-group-item">Reposts: <b>{data.reposts}</b></li>
                                <li className="list-group-item">Subscriptions: <b>{data.subscriptions}</b></li>
                                <li className="list-group-item">View: <b>{data.views}</b></li>
                            </ul>
                        </React.Fragment>
                    )}
                </React.Fragment>
            )}
        </div>
    );
}

export default connectToWidget('activity')(Activity);
