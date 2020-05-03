/* eslint-disable import/prefer-default-export */
export const booleanToRusString = (item) => {
    if (item === true) {
        return 'Да';
    }
    if (item === false) {
        return 'Нет';
    }
    return item;
};
