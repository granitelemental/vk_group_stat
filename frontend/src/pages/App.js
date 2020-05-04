import React from 'react';

import GearIcon from 'bootstrap-icons/icons/gear-fill.svg';

import TopPosts from 'widgets/TopPosts';
import Activity from 'widgets/Activity/index';
import Distribution from 'widgets/Distribution';

import './App.scss';

import Dashboard from 'components/Dashboard';

function App() {
    const widgets = [{
        Widget: TopPosts,
        grid: {
            x: 0,
            y: 0,
            w: 2,
            h: 4,
            minHeight: 4,
            i: 'topPosts',
        },
    }, {
        Widget: Activity,
        grid: {
            x: 2,
            y: 0,
            w: 1,
            h: 4,
            i: 'activity',
        },
    }, {
        Widget: Distribution,
        grid: {
            x: 0,
            y: 4,
            w: 2,
            h: 12,
            i: 'distribution',
        },
    }];

    return (
        <div className="App">
            <header className="Header">
                <div className="label label-success">
                    <img className="Header__avatar" alt="logo" src="https://sun9-10.userapi.com/c858328/v858328357/1ae57a/XGfbzRdzPWk.jpg?ava=1" />
                    Легущка
                </div>
                <div>
                    <img className="Icon" alt="settings" src={GearIcon} />
                </div>
            </header>
            <main>
                <div className="container">
                    <Dashboard widgets={widgets} />
                </div>
            </main>
        </div>
    );
}

export default App;
