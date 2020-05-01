import React from 'react';

import {getTopPosts} from 'api/routes';

import Spin from 'components/Spin';
import Widget from 'widgets/Widget'
import WidgetHeader from 'components/WidgetHeader';


import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
 
const options = {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
    },
    title: {
        text: 'Users by gender'
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
    },
    accessibility: {
        point: {
            valueSuffix: '%'
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                format: '<b>{point.name}</b>: {point.percentage:.1f} %'
            }
        }
    },
    series: [{
        name: 'Gender',
        colorByPoint: true,
        data: [{
            name: 'Male',
            y: 61,
            color: '',
        }, {
            name: 'Female',
            color: '#ff00e036',
            y: 37
        }, {
            name: 'Unknown',
            y: 2,
            color: 'grey'
        }]
    }]
};

// import './style.scss'

function TopPosts({isLoading, error, data}) {
    return (
        <div className="TopPosts">
           {isLoading ? <Spin/> : (
                <React.Fragment>
                    <WidgetHeader title="Пользователи" onSetup={() => {}} />
                    <HighchartsReact
                        highcharts={Highcharts}
                        options={options}
                    />
                </React.Fragment>
           )}
        </div>
    );
}

export default Widget(TopPosts, () => getTopPosts('1d'), [
    {id: 1, likes: 2, reposts: 12, comments: 3, views: 13},
    {id: 2, likes: 1, reposts: 2, comments: 0, views: 13},
    {id: 3, likes: 20, comments: 1, views: 13}
]);

