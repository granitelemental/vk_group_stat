import React from 'react';
import ReactDOM from 'react-dom';

import App from './pages/App';
import 'utils/vk';

import 'bootstrap/dist/css/bootstrap.min.css';
import './index.scss';

ReactDOM.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
    document.getElementById('root'),
);
