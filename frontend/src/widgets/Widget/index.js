import React from 'react';

export default (Component, fetcher, mock = false) => {
    return function WidgetWithState(props) {
        const [isLoading, setIsLoading] = React.useState(true);
        const [error, setError] = React.useState(null);
        const [data, setData] = React.useState([]);

        React.useEffect(() => {
            setIsLoading(true);
            fetcher().then((data) => {
                setData(data);
                setIsLoading(false);
            }).catch((err) => {
                if (mock) {
                    setData(mock);
                } else {
                    setError(err);
                }
                setIsLoading(false);
            });
        }, []);


        return <Component {...props} isLoading={isLoading} data={data} error={error} />;
    };
};
