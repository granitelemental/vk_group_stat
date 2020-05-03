export const formatDateToRusString = (date) => (date ? new Date(date).toLocaleDateString('ru', {year: 'numeric', month: 'long', day: 'numeric'}) : '');

export const formatDateToRusShortString = (date) => (date ? new Date(date).toLocaleDateString('ru', {month: 'long', day: 'numeric'}) : '');

export const formatDateToRusNumeric = (date) => (date ? new Date(date).toLocaleDateString('ru', {year: 'numeric', month: 'numeric', day: 'numeric'}) : '');

export const formatTimeFromDate = (date) => (date ? new Date(date).toLocaleTimeString().replace(/(\d{1,2}:\d{2}):\d{2}/, '$1') : '');

export const timeDifference = (start, end) => {
    const msPerMinute = 60 * 1000;
    const msPerHour = msPerMinute * 60;
    const msPerDay = msPerHour * 24;

    const difference = new Date(end) - new Date(start);
    const day = Math.floor(difference / msPerDay);
    const hour = Math.floor((difference - (day * msPerDay)) / msPerHour);
    const minute = Math.ceil((difference - (day * msPerDay + hour * msPerHour)) / msPerMinute);

    const dayStr = day ? `${day} дн ` : '';
    const hourStr = hour ? `${hour} час ` : '';
    const minStr = minute ? `${minute} мин` : '';

    return dayStr + hourStr + minStr;
};

export const getLastWeekRange = () => [new Date(new Date().setDate(new Date().getDate() - 6)), new Date()];

export const getLastMonthRange = () => [new Date(new Date().setMonth(new Date().getMonth() - 1)), new Date()];

export const getLastTwoMonthRange = () => [new Date(new Date().setMonth(new Date().getMonth() - 2)), new Date()];

export const formatDateToISOString = (date) => date.toISOString().slice(0, 10);

export const formatDatetoISOGMT = (date) => {
    const gmt = new Date(date).getTimezoneOffset() / 60;
    const gmtString = `${gmt < 0 ? '+' : '-'}${Math.abs(gmt) < 10 ? '0' : ''}${Math.abs(gmt)}:00`;
    const Iso = new Date(new Date(date).getTime() - (new Date(date).getTimezoneOffset() * 60000)).toISOString().split('.')[0];
    return encodeURIComponent(Iso + gmtString);
};

export const formatDateRange = (from, to, period) => {
    if (period === 'today') {
        return ({from: formatTimeFromDate(from), to: formatTimeFromDate(to)});
    }
    const start = new Date(from);
    const end = new Date(to);
    const sameYear = start.getFullYear() === end.getFullYear();
    const everyDay = (end.getDate() - start.getDate() === 1);
    const sameHours = (end.getHours() === start.getHours());
   
    if (!sameHours && sameYear) {
        return ({from: `${formatDateToRusShortString(from)} ${formatTimeFromDate(from)}`, to: `${formatDateToRusShortString(to)} ${formatTimeFromDate(to)}`});
    }
    if (!sameHours) {
        return ({from: `${formatDateToRusString(from)} ${formatTimeFromDate(from)}`, to: `${formatDateToRusString(to)} ${formatTimeFromDate(to)}`});
    }
    if (sameYear) {
        return everyDay ? ({from: formatDateToRusShortString(from)})
            : ({from: formatDateToRusShortString(from), to: formatDateToRusShortString(to)});
    }
    return ({from: formatDateToRusString(from), to: formatDateToRusString(to)});
};
