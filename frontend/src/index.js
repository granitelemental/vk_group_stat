import 'core-js';
import 'whatwg-fetch';
import React from 'react';
import ReactDOM from 'react-dom';

import Store from 'stores';
import {setStore} from 'tools/connect';
import makeInspectable from 'mobx-devtools-mst';

// import history from 'tools/history' // for router

import configs from 'configs';

import App from './pages/App';

import 'bootstrap/dist/css/bootstrap.min.css';
import './index.scss';


const store = Store.create({});
if (configs.environment !== 'production') {
    window.store = store;
    makeInspectable(store);
}
setStore(store);


ReactDOM.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
    document.getElementById('root'),
);
