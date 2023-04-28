#### Цели безопасности

1. Только авторизованный оператор-технолог в присутствии
оператора-безопасника может инициировать изменение настроек УД
2. Только авторизованный оператор-безопасник в присутствии
оператора-технолога может обновлять ПО УД
3. УД выдаёт целостные и достоверные данные во внешние системы с
задержкой не более 1 секунды в предположении, что операционная
система удовлетворяет требованиям обработки данных в реальном
времени
4. В УД применяются только целостные обновления

#### Предположения безопасности

1. Не рассматриваются атаки, связанные с физическим доступом к
оборудованию (например, подмена входных данных; подключение
имитатора УД и т.п.)
2. Не рассматриваются риски, связанные с физическим отказом внешнего
оборудования, включая обесточивание УД
3. Не рассматриваются риски, связанные с физическим отказом
аппаратного обеспечения устройства
4. Используется общий УЦ
5. Обновления в системе подписываются
6. СУЗ и АСУ ТП имеют блоки проверки подписи в общей системе открытых ключей УЦ

#### События безопасности

1. превышение входным сигналом порога предупреждения
2. превышение входным сигналом порога аварии
3. активация режима обновления системы
4. активация режима изменения настроек
5. изменение порога предупреждения
6. изменение порога аварии
