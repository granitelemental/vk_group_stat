import {useObserver} from 'mobx-react-lite';

let store = null;

export const setStore = (newStore) => {
    store = newStore;
};

const connect = (selector) => (baseComponent) => {
    /* eslint-disable */
    const component = (ownProps) => {
        if (store === null) throw new Error('Please, use setStore before your ReactDOM.render call');
        return useObserver(() => baseComponent({...ownProps, ...selector(store, ownProps)}));
    };
    /* eslint-enable */
    component.displayName = baseComponent.name;
    return component;
};

export default connect;
export const getStore = () => store;

export const connectToWidget = (name) => (component) => connect((s) => ({
    ...s.widgets.getWidget(name),
}))(component);
