import React from 'react';
import GearIcon from 'bootstrap-icons/icons/gear-fill.svg';

import {getTopPosts} from 'api/routes';

import PostWidget from 'components/PostWidget';
import Spin from 'components/Spin';
import Widget from 'widgets/Widget'
import ActivityMonitor from 'components/ActivityCounter'
import WidgetHeader from 'components/WidgetHeader';

import './style.scss'

function TopPosts({isLoading, error, data}) {
    return (
        <div className="TopPosts">
            {isLoading ? <Spin/> : (
                <React.Fragment>
                    <WidgetHeader title="Top 3 posts" onSetup={() => {}} />
                    {error ?  <h1>Ощибка</h1> : data.map((e) => {
                        return (
                            <div className="TopPosts__post">
                                Post ID: {e.id}
                                <ActivityMonitor {...e}/>
                            </div>
                        )
                    })}
                </React.Fragment>
           )}
        </div>
    );
}

export default Widget(TopPosts, () => getTopPosts('1d'));

