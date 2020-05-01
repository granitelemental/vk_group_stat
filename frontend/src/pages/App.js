import React from 'react';
import GearIcon from 'bootstrap-icons/icons/gear-fill.svg';

import {getTopPosts} from 'api/routes';

import TopPosts from 'widgets/TopPosts';
import Distribution from 'widgets/Distribution';
import Spacer from 'components/Spacer';

import './App.scss';

function App() {
    React.useEffect(() => {
        getTopPosts('1d').then(data => {

        }).catch(err => {
            
        })
        
    }, []);

    return (
        <div className="App">
            <header className="Header">
                <div className="label label-success">
                    <img className="Header__avatar" src="https://sun9-10.userapi.com/c858328/v858328357/1ae57a/XGfbzRdzPWk.jpg?ava=1" />
                    Легущка
                </div>
                <div>
                    <img className="Icon" src={GearIcon} />
                </div>
            </header>
            <main>
                <div className="container container-fluid">
                    <div className="row">
                        <div className="col-md-12">
                            <h1>Timeline</h1>
                            Тута будет график с таймлайном
                        </div>
                    </div>
                </div>
                <Spacer size={16} />
                <div className="container container-fluid">
                    <div className="row">
                        <div className="col-md-6">
                            <TopPosts />
                        </div>
                        <div className="col-md-6">
                            <h2>Daily activity</h2>
                            <ul class="list-group">
                                <li class="list-group-item">Posts: <b>3</b></li>
                                <li class="list-group-item">Likes: <b>13</b></li>
                                <li class="list-group-item">Comments: <b>7</b></li>
                                <li class="list-group-item">Reposts: <b>2</b></li>
                                <li class="list-group-item">Subscriptions: <b>2</b></li>
                            </ul>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6">
                            <Distribution />
                        </div>
                        <div className="col-md-6">
                            <h2>Daily activity</h2>
                            <ul className="list-group">
                                <li className="list-group-item">Posts: <b>3</b></li>
                                <li className="list-group-item">Likes: <b>13</b></li>
                                <li className="list-group-item">Comments: <b>7</b></li>
                                <li className="list-group-item">Reposts: <b>2</b></li>
                                <li className="list-group-item">Subscriptions: <b>2</b></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
