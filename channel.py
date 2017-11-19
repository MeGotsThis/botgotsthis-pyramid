import itertools
from contextlib import suppress
from datetime import timedelta
from typing import List, Optional  # noqa: F401

import bot

from lib.data import ChatCommandArgs
from lib.helper import chat, timeout
from lib.helper.chat import min_args, permission, permission_feature


@min_args(2)
@permission('broadcaster')
async def commandCPyramid(args: ChatCommandArgs) -> bool:
    count: int
    if 'cpyramid-' in args.message.command:
        try:
            count = int(args.message.command.split('cpyramid-')[1])
        except (ValueError, IndexError):
            count = 1
    else:
        count = None
    messages: List[str] = []
    if count is None:
        numWords: int = len(args.message.query.split())
        for i in range(numWords - 1, 0, -1):
            messages.append(args.message.query.rsplit(None, i)[0])
        for i in range(0, numWords):
            messages.append(args.message.query.rsplit(None, i)[0])
    else:
        msgs: List[str] = []
        numSpaces: int = 0
        for i in range(1, len(args.message.query)):
            if args.message.query[i - 1] == ' ':
                numSpaces += 1
                continue
            if (i - numSpaces) % count != 0:
                continue
            msgs.append(args.message.query[:i])
        messages = msgs + [args.message.query] + list(reversed(msgs))
    args.chat.send(messages, -1)
    if args.permissions.chatModerator:
        await timeout.record_timeout(args.chat, args.nick,
                                     messages[len(messages) // 2],
                                     str(args.message), 'cpyramid')
    return True


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
async def commandTacoPyramid(args: ChatCommandArgs) -> bool:
    count: int = 3 if args.permissions.broadcaster else 2
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[2])
    if len(args.message) == 1:
        rep: str = 'TBCheesePull'
    else:
        rep = args.message[1]
    return process_pyramid(args, 'TBTacoLeft', 'TBTacoRight', rep, count)


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandTacoPyramidLong(args: ChatCommandArgs) -> bool:
    count: int = 3 if args.permissions.broadcaster else 2
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('tacopyramid-')[1])
    return process_pyramid(args, 'TBTacoLeft', 'TBTacoRight',
                           args.message.query, count)


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandGivePyramid(args: ChatCommandArgs) -> bool:
    count: int = 3 if args.permissions.broadcaster else 2
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[2])
    return process_pyramid(args, 'GivePLZ', 'TakeNRG', args.message[1], count)


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandGivePyramidLong(args: ChatCommandArgs) -> bool:
    count: int = 3 if args.permissions.broadcaster else 2
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('givepyramid-')[1])
    return process_pyramid(args, 'GivePLZ', 'TakeNRG',
                           args.message.query, count)


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandTakePyramid(args: ChatCommandArgs) -> bool:
    count: int = 3 if args.permissions.broadcaster else 2
    # If below generate a ValueError or IndexError,
    # only the above line gets used
    with suppress(ValueError, IndexError):
        count = int(args.message[2])
    return process_pyramid(args, 'TakeNRG', 'GivePLZ', args.message[1], count)


@permission_feature(('broadcaster', None), ('moderator', 'modpyramid'))
@min_args(2)
async def commandTakePyramidLong(args: ChatCommandArgs) -> bool:
    count: int = 3 if args.permissions.broadcaster else 2
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('takepyramid-')[1])
    return process_pyramid(args, 'TakeNRG', 'GivePLZ',
                           args.message.query, count)


def process_pyramid(args: ChatCommandArgs,
                    prefix: str,
                    suffix: str,
                    repetition: str,
                    count: int) -> bool:
    limit: int = bot.config.messageLimit - (len(prefix) + 1 + len(suffix))
    count = min(count, limit // (len(repetition) + 1))
    if not args.permissions.broadcaster:
        count = min(count, 5)

        cooldown: timedelta = timedelta(
            seconds=bot.config.spamModeratorCooldown)
        if chat.inCooldown(args, cooldown, 'modPyramid'):
            return False
    elif not args.permissions.globalModerator:
        count = min(count, 20)
    messages: itertools.chain[str] = itertools.chain(
        (prefix + ' ' + ' '.join((repetition,) * i) + ' ' + suffix
         for i in range(1, count)),
        (prefix + ' ' + ' '.join((repetition,) * i) + ' ' + suffix
         for i in range(count, 0, -1)))
    args.chat.send(messages, -1)
    return True
