import pytest
import yaml
import os
from pathlib import Path


class TestWALListenerConfig:
    """Тесты для конфигурации WAL-listener"""

    def test_config_file_exists(self):
        """Тест существования конфигурационного файла"""
        config_path = Path(__file__).parent.parent / "config.yml"
        assert config_path.exists(), f"Конфигурационный файл не найден: {config_path}"

    def test_config_file_is_valid_yaml(self):
        """Тест валидности YAML файла"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f)
                assert config is not None, "Конфигурация не может быть пустой"
            except yaml.YAMLError as e:
                pytest.fail(f"Ошибка парсинга YAML: {e}")

    def test_listener_section_exists(self):
        """Тест наличия секции listener"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        assert 'listener' in config, "Секция 'listener' отсутствует в конфигурации"
        assert isinstance(config['listener'], dict), "Секция 'listener' должна быть словарем"

    def test_listener_slot_name(self):
        """Тест настройки slot name"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        listener_config = config['listener']
        assert 'slotName' in listener_config, "Параметр 'slotName' отсутствует"
        assert listener_config['slotName'] == 'wal_listener_slot', "Неверное значение slotName"

    def test_listener_refresh_connection(self):
        """Тест настройки refresh connection"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        listener_config = config['listener']
        assert 'refreshConnection' in listener_config, "Параметр 'refreshConnection' отсутствует"
        assert listener_config['refreshConnection'] == '30s', "Неверное значение refreshConnection"

    def test_listener_heartbeat_interval(self):
        """Тест настройки heartbeat interval"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        listener_config = config['listener']
        assert 'heartbeatInterval' in listener_config, "Параметр 'heartbeatInterval' отсутствует"
        assert listener_config['heartbeatInterval'] == '10s', "Неверное значение heartbeatInterval"

    def test_filter_section_exists(self):
        """Тест наличия секции filter"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        listener_config = config['listener']
        assert 'filter' in listener_config, "Секция 'filter' отсутствует"
        assert isinstance(listener_config['filter'], dict), "Секция 'filter' должна быть словарем"

    def test_filter_tables_section_exists(self):
        """Тест наличия секции tables в filter"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        filter_config = config['listener']['filter']
        assert 'tables' in filter_config, "Секция 'tables' отсутствует в filter"
        assert isinstance(filter_config['tables'], dict), "Секция 'tables' должна быть словарем"

    def test_filter_tables_contains_required_tables(self):
        """Тест наличия всех необходимых таблиц"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        tables_config = config['listener']['filter']['tables']
        required_tables = ['promo_offer', 'promo_category', 'promo_city', 'promo_partner']
        
        for table in required_tables:
            assert table in tables_config, f"Таблица '{table}' отсутствует в конфигурации"

    def test_filter_tables_actions(self):
        """Тест действий для таблиц"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        tables_config = config['listener']['filter']['tables']
        required_actions = ['insert', 'update', 'delete']
        
        for table_name, table_config in tables_config.items():
            assert isinstance(table_config, list), f"Конфигурация таблицы '{table_name}' должна быть списком"
            for action in required_actions:
                assert action in table_config, f"Действие '{action}' отсутствует для таблицы '{table_name}'"

    def test_topics_map_section_exists(self):
        """Тест наличия секции topicsMap"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        listener_config = config['listener']
        assert 'topicsMap' in listener_config, "Секция 'topicsMap' отсутствует"
        assert isinstance(listener_config['topicsMap'], dict), "Секция 'topicsMap' должна быть словарем"

    def test_topics_map_mapping(self):
        """Тест маппинга топиков"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        topics_map = config['listener']['topicsMap']
        expected_mapping = {
            'public_promo_offer': 'promo_offers',
            'public_promo_category': 'promo_categories',
            'public_promo_city': 'cities',
            'public_promo_partner': 'partners'
        }
        
        for table, topic in expected_mapping.items():
            assert table in topics_map, f"Маппинг для таблицы '{table}' отсутствует"
            assert topics_map[table] == topic, f"Неверный топик для таблицы '{table}'"

    def test_include_old_new_values(self):
        """Тест настроек includeOldValues и includeNewValues"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        listener_config = config['listener']
        assert 'includeOldValues' in listener_config, "Параметр 'includeOldValues' отсутствует"
        assert 'includeNewValues' in listener_config, "Параметр 'includeNewValues' отсутствует"
        assert listener_config['includeOldValues'] is True, "includeOldValues должен быть True"
        assert listener_config['includeNewValues'] is True, "includeNewValues должен быть True"

    def test_logger_section_exists(self):
        """Тест наличия секции logger"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        assert 'logger' in config, "Секция 'logger' отсутствует"
        assert isinstance(config['logger'], dict), "Секция 'logger' должна быть словарем"

    def test_logger_configuration(self):
        """Тест конфигурации логгера"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        logger_config = config['logger']
        assert 'level' in logger_config, "Параметр 'level' отсутствует в logger"
        assert 'fmt' in logger_config, "Параметр 'fmt' отсутствует в logger"
        assert logger_config['level'] == 'info', "Уровень логирования должен быть 'info'"
        assert logger_config['fmt'] == 'json', "Формат логирования должен быть 'json'"

    def test_database_section_exists(self):
        """Тест наличия секции database"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        assert 'database' in config, "Секция 'database' отсутствует"
        assert isinstance(config['database'], dict), "Секция 'database' должна быть словарем"

    def test_database_configuration(self):
        """Тест конфигурации базы данных"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        db_config = config['database']
        required_params = ['host', 'port', 'name', 'user', 'password', 'debug']
        
        for param in required_params:
            assert param in db_config, f"Параметр '{param}' отсутствует в конфигурации БД"
        
        assert db_config['host'] == 'db', "Хост БД должен быть 'db'"
        assert db_config['port'] == 5432, "Порт БД должен быть 5432"
        assert db_config['name'] == 'ufanet_db', "Имя БД должно быть 'ufanet_db'"
        assert db_config['user'] == 'user', "Пользователь БД должен быть 'user'"
        assert str(db_config['password']) == '111', "Пароль БД должен быть '111'"
        assert db_config['debug'] is False, "Debug должен быть False"

    def test_publisher_section_exists(self):
        """Тест наличия секции publisher"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        assert 'publisher' in config, "Секция 'publisher' отсутствует"
        assert isinstance(config['publisher'], dict), "Секция 'publisher' должна быть словарем"

    def test_publisher_configuration(self):
        """Тест конфигурации publisher"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        publisher_config = config['publisher']
        assert 'type' in publisher_config, "Параметр 'type' отсутствует в publisher"
        assert 'address' in publisher_config, "Параметр 'address' отсутствует в publisher"
        assert 'topic' in publisher_config, "Параметр 'topic' отсутствует в publisher"
        assert 'topicPrefix' in publisher_config, "Параметр 'topicPrefix' отсутствует в publisher"
        
        assert publisher_config['type'] == 'kafka', "Тип publisher должен быть 'kafka'"
        assert publisher_config['address'] == 'kafka:9092', "Адрес Kafka должен быть 'kafka:9092'"
        assert publisher_config['topic'] == 'wal_listener', "Топик должен быть 'wal_listener'"
        assert publisher_config['topicPrefix'] == '', "Префикс топика должен быть пустым"

    def test_monitoring_section_exists(self):
        """Тест наличия секции monitoring"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        assert 'monitoring' in config, "Секция 'monitoring' отсутствует"
        assert isinstance(config['monitoring'], dict), "Секция 'monitoring' должна быть словарем"

    def test_monitoring_configuration(self):
        """Тест конфигурации monitoring"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        monitoring_config = config['monitoring']
        assert 'promAddr' in monitoring_config, "Параметр 'promAddr' отсутствует в monitoring"
        assert monitoring_config['promAddr'] == ':2112', "Адрес Prometheus должен быть ':2112'"

    def test_config_structure_completeness(self):
        """Тест полноты структуры конфигурации"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Проверяем, что нет лишних секций
        expected_sections = ['listener', 'logger', 'database', 'publisher', 'monitoring']
        actual_sections = list(config.keys())
        
        for section in expected_sections:
            assert section in actual_sections, f"Секция '{section}' отсутствует"
        
        # Проверяем, что нет неожиданных секций
        for section in actual_sections:
            assert section in expected_sections, f"Неожиданная секция '{section}'"

    def test_config_file_permissions(self):
        """Тест прав доступа к конфигурационному файлу"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        assert config_path.exists(), "Конфигурационный файл не существует"
        assert config_path.is_file(), "Конфигурационный файл не является файлом"
        assert os.access(config_path, os.R_OK), "Конфигурационный файл недоступен для чтения"

    def test_config_file_encoding(self):
        """Тест кодировки конфигурационного файла"""
        config_path = Path(__file__).parent.parent / "config.yml"
        
        # Пробуем прочитать файл в разных кодировках
        encodings = ['utf-8', 'utf-8-sig', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(config_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    yaml.safe_load(content)
                break
            except UnicodeDecodeError:
                continue
        else:
            pytest.fail("Не удалось прочитать файл ни в одной из кодировок") 