from unittest import TestCase

from pyminehub.mcpe.command import *


class CommandProcessor:

    @command
    def ban(self, player_name: RawText) -> str:
        """Prevents the specified player from using this server"""
        return 'ban player by name {}'.format(player_name)

    @ban.overload
    def ban(self, player_id: Int) -> str:
        return 'ban player by id {}'.format(player_id)

    @ban.overload
    def ban(self, player_name: RawText, player_id: Int) -> str:
        return 'ban player by name {} and id {}'.format(player_name, player_id)

    @ban.overload
    def ban(self) -> str:
        return 'ban all players'

    @command
    def tell(self, message: RawText, lang: RawText='en') -> str:
        return 'tell {} in {}'.format(message, lang)

    @command
    def kill(self, player_id: RawText) -> None:
        """"""
        pass

    @command
    def version(self, value: RawText=''):
        """Gets the version of this server including any plugins in use

        Some description.
        """
        pass

    # aliases
    w = tell
    suicide = kill
    ver = version
    about = version
    msg = tell


class CommandProcessorDuplicated1:

    @command
    def ban(self) -> None:
        pass


class CommandProcessorDuplicated2:

    @command
    def say(self) -> None:
        pass

    msg = say


class CommandTestCase(TestCase):

    def test_command(self):
        registry = CommandRegistry()
        processor = CommandProcessor()
        registry.register_command_processor(processor)

        self.assertEqual('ban player by name taro', processor.ban('taro'))
        self.assertEqual('ban player by id 1234', processor.ban(1234))
        self.assertEqual('ban player by name suzuki and id 51', processor.ban('suzuki', 51))
        self.assertEqual('ban all players', processor.ban())
        self.assertEqual('tell hi in en', processor.w('hi'))
        self.assertEqual('tell hello in english', processor.msg('hello', 'english'))

        expected_spec = CommandSpec(
            enum_values=('suicide', 'msg', 'w', 'about', 'ver'),
            postfixes=(),
            enums=(
                CommandEnum(name='kill_aliases', index=(0,)),
                CommandEnum(name='tell_aliases', index=(1, 2)),
                CommandEnum(name='version_aliases', index=(3, 4))
            ),
            command_data=(
                CommandData(
                    name='ban', description='Prevents the specified player from using this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='player_name', type=1048593, is_optional=False),
                        ),
                        (
                            CommandParameter(name='player_id', type=1048577, is_optional=False),
                        ),
                        (
                            CommandParameter(name='player_name', type=1048593, is_optional=False),
                            CommandParameter(name='player_id', type=1048577, is_optional=False)
                        ),
                        ()
                    )
                ),
                CommandData(
                    name='kill', description='no description',
                    flags=0, permission=0, aliases=0,
                    overloads=(
                        (
                            CommandParameter(name='player_id', type=1048593, is_optional=False),
                        ),
                    )
                ),
                CommandData(
                    name='tell', description='no description',
                    flags=0, permission=0, aliases=1,
                    overloads=(
                        (
                            CommandParameter(name='message', type=1048593, is_optional=False),
                            CommandParameter(name='lang', type=1048593, is_optional=True)
                        ),
                    )
                ),
                CommandData(
                    name='version', description='Gets the version of this server including any plugins in use',
                    flags=0, permission=0, aliases=2,
                    overloads=(
                        (
                            CommandParameter(name='value', type=1048593, is_optional=True),
                        ),
                    )
                )
            ),
            permission=CommandPermission.NORMAL
        )
        self.assertEqual(expected_spec, registry.get_command_spec())

        self.assertEqual('ban player by name taro', registry.execute_command('ban', 'taro'))
        self.assertEqual('ban player by id 1234', registry.execute_command('ban', 1234))
        self.assertEqual('ban player by name suzuki and id 51', registry.execute_command('ban', 'suzuki', 51))
        self.assertEqual('ban all players', registry.execute_command('ban'))
        self.assertEqual('tell hi in en', registry.execute_command('w', 'hi'))
        self.assertEqual('tell hello in english', registry.execute_command('msg', 'hello', 'english'))

    def test_command_duplicate(self):
        registry = CommandRegistry()
        registry.register_command_processor(CommandProcessor())
        with self.assertRaises(DuplicateDefinitionError):
            registry.register_command_processor(CommandProcessorDuplicated1())

        registry = CommandRegistry()
        registry.register_command_processor(CommandProcessor())
        with self.assertRaises(DuplicateDefinitionError):
            registry.register_command_processor(CommandProcessorDuplicated2())


if __name__ == '__main__':
    import unittest
    unittest.main()
