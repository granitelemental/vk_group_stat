import React from 'react';

import './style.scss'

export default function ActivityCounter({likes, reposts, comments, views}) {
    return (
        <div className="ActivityCounter">
            {[[likes, 'likes'], [reposts, 'reposts'], [comments, 'comments'], [views, 'views']]
                .map(([item, cls]) => {
                    if (!item) {return null}
                    return (
                        <span className="ActivityCounter__item" key={cls}>
                            <span className={`ActivityCounter__icon ActivityCounter__icon_${cls}`} />
                            <span className="ActivityCounter__count">
                                {item}
                            </span>
                        </span>
                    )
                })
            }
        </div>
    )
};
