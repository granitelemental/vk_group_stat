import React from 'react';
import GearIcon from 'bootstrap-icons/icons/gear-fill.svg';

import {getTopPosts} from 'api/routes';

import PostWidget from 'components/PostWidget';

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
                <div className="label label-success">Group ID</div>
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
                <div className="container container-fluid">
                    <div className="row">
                        <div className="col-md-6">
                            <h2>Top posts</h2>
                            <PostWidget wallId={'193519310_45'} />
                        </div>
                        <div className="col-md-6">
                            <h2>Daily activity</h2>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
