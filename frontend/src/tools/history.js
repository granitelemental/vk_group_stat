import {createBrowserHistory} from 'history';
import config from 'configs';

export default createBrowserHistory({basename: config.newAppBaseUrl});
