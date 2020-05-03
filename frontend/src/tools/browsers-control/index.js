import detect from './detect';
import html from './browser';

if (process.env.NODE_ENV !== 'test') {
    window.UserAgent = detect.parse(navigator.userAgent);
}

const browsersContol = {
    browserVerify() {
        if (process.env.NODE_ENV === 'test') {
            return {
                isNotAllowedBrowser: false,
            };
        }

        const userBrowser = {
            browserName: window.UserAgent.browser.family,
            browserVersion: window.UserAgent.browser.version,
            source: window.UserAgent.source,
        };
        const isIe = userBrowser.browserName === 'IE';
        const nodeElement = document.createElement('div');
        nodeElement.setAttribute('id', 'for_bad_users');
        nodeElement.innerHTML = html;

        const allowedBrowsers = [
            {
                name: 'Chrome',
                minVersion: '21',
            },
            {
                name: 'IE',
                minVersion: '11',
            },
            {
                name: 'Firefox',
                minVersion: '18',
            },
            {
                name: 'Opera',
                minVersion: '17',
            },
            {
                name: 'Safari',
                minVersion: '6.1',
            },
        ];

        const isNotAllowedBrowser = allowedBrowsers.some(
            (chackBrowser) => chackBrowser.name === userBrowser.browserName && +chackBrowser.minVersion > +userBrowser.browserVersion,
        );

        return {
            isNotAllowedBrowser,
            nodeElement,
            isIe,
            userBrowser,
        };
    },
};

export default browsersContol;
