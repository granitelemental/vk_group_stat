import React from 'react';

export default function Post({wallId}) {
    React.useEffect(() => {
        const VK = window.VK;
        const [pId, id] = wallId.slice('_');

        VK && VK.Widgets && VK.Widgets.Post && window.VK.Widgets.Post("vk_post_" + wallId, pId, id, 'ZMk4b98xpQZMJJRXVsL1ig', {width: 500});
    })

    return (
        <div className="PostWidget">
            <div id={`vk_post_${wallId}`}></div>
        </div>
    );
}