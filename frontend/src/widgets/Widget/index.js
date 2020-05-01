import React from 'react';

export default (Component, fetcher, mock = false) => {
    return function WidgetWithState(props) {
        const [isLoading, setIsLoading] = React.useState(true);
        const [error, setError] = React.useState(null);
        const [data, setData] = React.useState(true);
        React.useEffect(() => {

            setIsLoading(true);
            fetcher().then(data => {
                setData(data);
                setIsLoading(false);
            }).catch(err => {
                mock ? setData(mock) : setError(err);
                setIsLoading(false);

            })
            
        }, []);


        return <Component isLoading={isLoading} data={data} error={error} />
    }
}