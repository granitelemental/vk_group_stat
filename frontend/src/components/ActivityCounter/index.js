import React from 'react';

import './style.scss'

export default function ActivityCounter({likesCount, repostsCount, commentsCount, viewsCount}) {
    const fields = [
        [likesCount, 'likes'],
        [repostsCount, 'reposts'],
        [commentsCount, 'comments'],
        [viewsCount, 'views']
    ];

    return (
        <div className="ActivityCounter">
            {fields
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
