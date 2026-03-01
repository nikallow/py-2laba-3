# Лабораторная работа №1. Источники задач и контракты

## Цель
Освоение Duck Typing и контрактов,
реализовать сборщик и обработчик тасков из разных источников, объединённых контрактом.

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
- Dataclass `Task` с `id` и `payload`.
- `TaskSource` - определение контракта. Любой объект, имеющий метод `get_tasks() -> Iterable[Task]` считается валидным источником.

`src/sources/*`
- `FileTaskSource`: Считывает задачи из текстовых файлов (одна строка — одна задача).
- `APITaskSource`: Имитирует получение данных из внешнего API.
- `RandomTaskGenerator`: Программная генерация случайных задач.

* `src/registry.py` `TaskRegistry` Регистрации источников. Использует `isinstance(source, TaskSource)` для обеспечения безопасности типов перед добавлением сурца в реестр.
* `src/processor.py` `TaskProcessor` Тупо обработчик.

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
│       ├── __init__.py
│       └── task.py
├── tests
│   ├── test_api_src.py
│   ├── test_file_src.py
│   ├── test_gen_src.py
│   └── test_registry.py
└── uv.lock
```
