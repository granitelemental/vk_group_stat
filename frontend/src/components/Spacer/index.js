import React from 'react';
import PropTypes from 'prop-types';

const Spacer = ({size = 8, className = ''}) => {
    return <div style={{height: size}} className={className} />;
};

Spacer.propTypes = {
    size: PropTypes.number,
    className: PropTypes.string,
};

export default Spacer;
