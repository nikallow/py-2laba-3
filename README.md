# Лабораторная работа №3. Очередь задач: итераторы и генераторы

## Цель

- реализовать пользовательскую коллекцию `TaskQueue`, поддерживающую итерацию
- обеспечить повторный обход очереди и корректное завершение итерации (`StopIteration`)
- применить генераторы для ленивой фильтрации задач
- показать совместимость коллекции со стандартными конструкциями Python (ex: `for`, `list`)
- обеспечить корректную работу на больших данных

## Installation and launching

#### Just

```shell
just install
just run
```

#### No just

```shell
uv sync
uv run python -m src.main
```


## Архитектура
`src/tasks/task.py`

- `Task` - Реализует доменную модель задачи, используя дескрипторы для управления доступом
  к атрибутам (id, description, priority, status, created_at)
  и для защиты инвариантов состояния. Включает вычисляемые свойства (@property) и
  методы для управления жизненным циклом задачи (смена статусов: mark_ready, start, complete, cancel),
  генерирующие специализированные исключения при нарушении инвариантов.
- `TaskSource` - определение контракта. Любой объект, имеющий метод `get_tasks() -> Iterable[Task]` считается валидным источником.

`src/tasks/descriptors.py`

- Классы-дескрипторы: Набор дескрипторов (NonEmptyString, PriorityDescriptor, StatusDescriptor, CreatedAtDescriptor,
  ModelInfoDescriptor),
  которые обеспечивают валидацию, контроль типов и защиту атрибутов класса Task от некорректных значений или изменений.

`src/tasks/enums.py`

- `TaskStatus` - Определяет допустимые состояния задачи (NEW, READY, IN_PROGRESS, DONE, BLOCKED, CANCELLED) и
  предоставляет методы для безопасного преобразования значений.

`src/tasks/queue.py`

- `TaskQueue` хранит зарегистрированные источники и реализует `__iter__`
- обход задач сделан через `yield from` (ленивая потоковая выдача)
- `filter_by_status`, `filter_by_priority`, `filter_higher_priority` возвращают генераторы
- фильтрация выполняется без материализации всей очереди в память

`src/sources/*`
- `FileTaskSource`: Считывает задачи из текстовых файлов (одна строка — одна задача).
- `APITaskSource`: Имитирует получение данных из внешнего API.
- `RandomTaskGenerator`: Программная генерация случайных задач.

`src/processor.py`

- `TaskProcessor` выполняет базовую обработку задачи и переходы по статусам.

## Тесты (Queue)

Тесты для очереди находятся в `tests/test_task_queue.py`:

- добавление валидного/невалидного источника
- итерация по задачам и устойчивость к исключениям источника
- повторный обход очереди
- явный `StopIteration` на пустой очереди
- ленивые фильтры по статусу/приоритету и валидация ошибок ввода

## Tree

```text
.
├── justfile
├── pyproject.toml
├── README.md
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── processor.py
│   ├── sources
│   │   ├── api_src.py
│   │   ├── file_src.py
│   │   └── gen_src.py
│   └── tasks
│       ├── __init__.py
│       ├── descriptors.py
│       ├── enums.py
│       ├── exceptions.py
│       ├── queue.py
│       ├── task.py
│       └── validators.py
├── tests
│   ├── test_api_src.py
│   ├── test_descriptors.py
│   ├── test_file_src.py
│   ├── test_gen_src.py
│   ├── test_processor.py
│   └── test_task_queue.py
└── uv.lock
```
