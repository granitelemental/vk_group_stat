import React from 'react';

import './style.scss';

export default function Spin() {
    return (
        <span className="Spin">
            <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                <g transform="translate(50 50)">
                    <g transform="scale(1)">
                        <g transform="translate(-50 -50)">
                            <g transform="rotate(218.322 50 50)">
                                <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" values="0 50 50;360 50 50" keyTimes="0;1" dur="0.8620689655172414s" />
                                <path fillOpacity="0.9" fill="#e15b64" d="M50 50L50 0A50 50 0 0 1 100 50Z" />
                            </g>
                            <g transform="rotate(73.7398 50 50)">
                                <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" values="0 50 50;360 50 50" keyTimes="0;1" dur="1.149425287356322s" />
                                <path fillOpacity="0.9" fill="#d48be8" d="M50 50L50 0A50 50 0 0 1 100 50Z" transform="rotate(90 50 50)" />
                            </g>
                            <g transform="rotate(289.16 50 50)">
                                <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" values="0 50 50;360 50 50" keyTimes="0;1" dur="1.7241379310344829s" />
                                <path fillOpacity="0.9" fill="#896af8" d="M50 50L50 0A50 50 0 0 1 100 50Z" transform="rotate(180 50 50)" />
                            </g>
                            <g transform="rotate(144.58 50 50)">
                                <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" values="0 50 50;360 50 50" keyTimes="0;1" dur="3.4482758620689657s" />
                                <path fillOpacity="0.9" fill="#fef26b" d="M50 50L50 0A50 50 0 0 1 100 50Z" transform="rotate(270 50 50)" />
                            </g>
                        </g>
                    </g>
                </g>
            </svg>
        </span>
    );
}
