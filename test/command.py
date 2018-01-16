from unittest import TestCase

from pyminehub.mcpe.command import *
from pyminehub.mcpe.const import GameMode
from util.mock import MockCommandContext


class CommandProcessor:

    @command
    def ban(self, context: CommandContext, args: str) -> None:
        """Prevents the specified player from using this server"""
        try:
            self._ban(context, Int(args))
        except ValueError:
            self._ban(context, Message(args))

    @ban.overload
    def _ban(self, context: CommandContext, player_name: Message) -> None:
        context.send_text('ban by name = {}'.format(player_name))

    @ban.overload
    def _ban(self, context: CommandContext, player_id: Int) -> None:
        context.send_text('ban by id = {}'.format(player_id))

    @ban.overload
    def _ban(self, player_name: Message, player_id: Int) -> None:
        pass  # NOTE this method is called from ban

    @ban.overload
    def _ban(self) -> None:
        pass  # NOTE this method is called from ban

    @command
    def tell(self, context: CommandContext, args: str) -> None:
        # no description
        context.send_text('tell {}'.format(args))

    @tell.overload
    def _tell(self, message: Message, lang: Message= 'en') -> None:
        pass  # NOTE this method is called from tell

    @command
    def kill(self, context: CommandContext, args: str) -> None:
        """"""
        pass

    @kill.overload
    def _kill(self, player_id: Message) -> None:
        pass  # NOTE this method is called from kill

    @command
    def version(self, context: CommandContext, args: str) -> None:
        """Gets the version of this server including any plugins in use

        Some description.
        """
        pass

    @version.overload
    def _version(self, context: CommandContext, value: Message= '') -> None:
        pass  # NOTE this method is called from version

    # aliases
    w = tell
    suicide = kill
    ver = version
    about = version
    msg = tell


class CommandProcessorDuplicated1:

    @command
    def ban(self, context: CommandContext, args: str) -> None:
        pass


class CommandProcessorDuplicated2:

    @command
    def say(self, context: CommandContext, args: str) -> None:
        pass

    msg = say


class CommandProcessorEnum:

    @command
    def game_mode(self, context: CommandContext, args: str) -> None:
        context.send_text(str(context.get_enum_value(args)))

    @game_mode.overload
    def _game_mode(self, mode: GameMode) -> None:
        pass


class CommandTestCase(TestCase):

    def test_command(self):
        registry = CommandRegistry()
        processor = CommandProcessor()
        registry.register_command_processor(processor)

        context = MockCommandContext(registry)
        processor.ban(context, 'taro')
        self.assertEqual('ban by name = taro', context.text)
        processor.ban(context, '1')
        self.assertEqual('ban by id = 1', context.text)
        processor.w(context, 'hi')
        self.assertEqual('tell hi', context.text)
        processor.msg(context, 'hello')
        self.assertEqual('tell hello', context.text)

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
                            # there is not context parameter
                            CommandParameter(name='value', type=1048593, is_optional=True),
                        ),
                    )
                )
            ),
            permission=CommandPermission.NORMAL
        )
        self.assertEqual(expected_spec, registry.get_command_spec())

        context = MockCommandContext(registry)
        registry.execute_command(context, 'ban', 'taro')
        self.assertEqual('ban by name = taro', context.text)
        registry.execute_command(context, 'ban', '1')
        self.assertEqual('ban by id = 1', context.text)
        registry.execute_command(context, 'w', 'hi')
        self.assertEqual('tell hi', context.text)
        registry.execute_command(context, 'msg', 'hello')
        self.assertEqual('tell hello', context.text)

    def test_command_duplicate(self):
        registry = CommandRegistry()
        registry.register_command_processor(CommandProcessor())
        with self.assertRaises(DuplicateDefinitionError):
            registry.register_command_processor(CommandProcessorDuplicated1())

        registry = CommandRegistry()
        registry.register_command_processor(CommandProcessor())
        with self.assertRaises(DuplicateDefinitionError):
            registry.register_command_processor(CommandProcessorDuplicated2())

    def test_enum(self):
        registry = CommandRegistry()
        processor = CommandProcessorEnum()
        registry.register_command_processor(processor)

        context = MockCommandContext(registry)
        processor.game_mode(context, 'creative')
        self.assertEqual(str(GameMode.CREATIVE), context.text)

        expected_spec = CommandSpec(
            enum_values=('survival', 'creative', 'adventure'),
            postfixes=(),
            enums=(
                CommandEnum(name='GameMode', index=(0, 1, 2)),
            ),
            command_data=(
                CommandData(
                    name='game_mode', description='no description',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='mode', type=3145728, is_optional=False),
                        ),
                    )
                ),
            ),
            permission=CommandPermission.NORMAL
        )
        self.assertEqual(expected_spec, registry.get_command_spec())

        registry.execute_command(context, 'game_mode', 'creative')
        self.assertEqual(str(GameMode.CREATIVE), context.text)


if __name__ == '__main__':
    import unittest
    unittest.main()
