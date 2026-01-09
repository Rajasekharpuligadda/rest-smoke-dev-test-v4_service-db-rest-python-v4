"""
PostgreSQL extension for Flask application.

This module provides PostgreSQL database connection management with connection pooling
and health checking capabilities.
"""

from typing import Optional, Dict, Any, List
from flask import Flask, current_app
from contextlib import contextmanager
import asyncio
import asyncpg
from app.logger import logger


class PostgreSQLManager:
    """
    PostgreSQL connection manager with both sync and async support using asyncpg.
    """

    def __init__(self, app: Optional[Flask] = None):
        self.config: Optional[Dict[str, Any]] = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize PostgreSQL connection with the Flask app.

        Args:
            app: Flask application instance
        """
        try:
            # Store configuration
            self.config = {
                'host': app.config.get('POSTGRES_HOST', 'localhost'),
                'port': app.config.get('POSTGRES_PORT', 5432),
                'database': app.config.get('POSTGRES_DB', 'dafault'),
                'user': app.config.get('POSTGRES_USER', 'postgres'),
                'password': app.config.get('POSTGRES_PASSWORD', ''),
            }

            # Test the connection
            self._test_connection()

            # Store manager in app extensions
            if not hasattr(app, 'extensions'):
                app.extensions = {}
            app.extensions['postgres'] = self

            logger.info("PostgreSQL connection initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {e}")
            raise

    def _test_connection(self) -> None:
        if not self.config:
            raise Exception("PostgreSQL configuration not available")

        # Run async test in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._async_test_connection())
        finally:
            loop.close()

        logger.info("PostgreSQL connection test successful")

    async def _async_test_connection(self) -> None:
        conn = await asyncpg.connect(**self.config)
        try:
            await conn.fetchval("SELECT 1")
        finally:
            await conn.close()

    def get_config(self) -> Dict[str, Any]:
        if self.config:
            return self.config
        else:
            raise Exception("No PostgreSQL configuration available")

    @contextmanager
    def get_connection(self):
        """
        Get a database connection (sync wrapper around async).

        Yields:
            Database connection

        Example:
            with postgres_manager.get_connection() as conn:
                result = await conn.fetch("SELECT * FROM users")
        """
        config = self.get_config()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            conn = loop.run_until_complete(asyncpg.connect(**config))
            yield conn
        finally:
            if 'conn' in locals():
                loop.run_until_complete(conn.close())
            loop.close()

    def execute_query(self, query: str, *args) -> List[Any]:
        """
        Execute a SQL query and return results (sync wrapper).

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Query results
        """
        config = self.get_config()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            conn = loop.run_until_complete(asyncpg.connect(**config))
            try:
                return loop.run_until_complete(conn.fetch(query, *args))
            finally:
                loop.run_until_complete(conn.close())
        finally:
            loop.close()

    def health_check(self) -> Dict[str, Any]:
        try:
            config = self.get_config()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                conn = loop.run_until_complete(asyncpg.connect(**config))
                try:
                    result = loop.run_until_complete(conn.fetchval("SELECT 1"))
                    if result == 1:
                        return {
                            "status": "healthy",
                            "message": "PostgreSQL connection is working"
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": "Health check query returned unexpected result"
                        }
                finally:
                    loop.run_until_complete(conn.close())
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def get_async_connection(self, config: Optional[Dict[str, Any]] = None):
        """
        Get an async database connection using asyncpg.

        Args:
            config: Optional configuration dict. If not provided, uses stored config.

        Returns:
            AsyncPG connection

        Example:
            conn = await postgres_manager.get_async_connection()
            result = await conn.fetch("SELECT * FROM users")
            await conn.close()
        """
        if config is None:
            config = self.get_config()

        return await asyncpg.connect(**config)

    async def execute_async_query(self, query: str, *args, config: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Execute an async SQL query and return results.

        Args:
            query: SQL query string
            *args: Query parameters
            config: Optional configuration dict

        Returns:
            Query results
        """
        conn = await self.get_async_connection(config)
        try:
            return await conn.fetch(query, *args)
        finally:
            await conn.close()

    async def health_check_async(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform an async health check on the PostgreSQL connection.

        Args:
            config: Optional configuration dict

        Returns:
            Dictionary with health status information
        """
        try:
            conn = await self.get_async_connection(config)
            try:
                result = await conn.fetchval("SELECT 1")
                if result == 1:
                    return {
                        "status": "healthy",
                        "message": "PostgreSQL connection is working"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "Health check query returned unexpected result"
                    }
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"PostgreSQL async health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global instance
postgres_manager = PostgreSQLManager()

def init_postgres(app: Flask) -> None:
    postgres_manager.init_app(app)


def get_postgres_manager() -> PostgreSQLManager:
    return postgres_manager



