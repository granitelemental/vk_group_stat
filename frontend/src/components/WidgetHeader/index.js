import React from 'react';
import Gear from 'bootstrap-icons/icons/gear.svg';

import './style.scss'

function WidgetHeader({title, className='', onSetup}) {
    return (
        <div className={`WidgetHeader ${className}`}>
            <h3 className="WidgetHeader__title">{title}</h3>
            {onSetup && typeof onSetup === 'function' && <img className="WidgetHeader__icon" src={Gear} onClick={onSetup} />}
            <hr className="WidgetHeader__hr"/>
        </div>
    );
}

export default WidgetHeader;


