# Лабораторная работа №2. Модель задачи: дескрипторы и `@property`

## Цель

- изучить механизм **data** и **non-data descriptors**;
- применить `@property` для вычисляемых свойств;
- предотвратить некорректные состояния доменной модели;
- использовать специализированные исключения для нарушения инвариантов.

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

`src/sources/*`
- `FileTaskSource`: Считывает задачи из текстовых файлов (одна строка — одна задача).
- `APITaskSource`: Имитирует получение данных из внешнего API.
- `RandomTaskGenerator`: Программная генерация случайных задач.

* `src/registry.py` `TaskRegistry` Регистрации источников. Использует `isinstance(source, TaskSource)` для обеспечения безопасности типов перед добавлением сурца в реестр.
* `src/processor.py` `TaskProcessor` Тупой обработчик.

## Tree
```
.
├── justfile
├── pyproject.toml
├── README.md
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── processor.py
│   ├── registry.py
│   ├── sources
│   │   ├── api_src.py
│   │   ├── file_src.py
│   │   └── gen_src.py
│   └── tasks
│       ├── descriptors.py
│       ├── enums.py
│       ├── exceptions.py
│       ├── __init__.py
│       └── task.py
├── tests
│   ├── test_api_src.py
│   ├── test_descriptors.py
│   ├── test_file_src.py
│   ├── test_gen_src.py
│   ├── test_processor.py
│   └── test_registry.py
└── uv.lock
```
