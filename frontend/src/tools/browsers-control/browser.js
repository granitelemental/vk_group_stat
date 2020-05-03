const browserException = '<div class="browserException">'
    + '<img class="browserException__img" src="'
    + process.env.PUBLIC_URL
    + '/images/group.png">'
    + '<div class="browserException__content">'
    + '<div class="browserException__title">Уважаемый пользователь!</div>'
    + '<div class="browserException__paragraph">Версия вашего браузера не поддерживается системой.<br>'
    + 'Для входа в АТОЛ ЛК обновите версию <b>Internet Explorer</b> до 11 или выше.<br>'
    + '</div>'
    + '<div class="browserException__divider"><span>или</span></div>'
    + '<div class="browserException__subtitle">Воспользуйтесь одним из браузеров:</div>'
    + '<ul>'
    + '<li>Google Chrome</li>'
    + '<li>Opera</li>'
    + '<li>Mozilla Firefox</li>'
    + '<li>Яндекс</li>'
    + '</ul>'
    + '</div>'
    + '</div>';

export default browserException;
