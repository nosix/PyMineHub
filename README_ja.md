# PyMineHub (PMH)

マインクラフト (モバイル版) マルチプレイサーバー

このプロジェクトの目指すところは、サーバーを小さく保ちつつ、他の様々な仕組みと接続できるようにすることです。
マインクラフトの全仕様を実装するよりは、拡張できる仕組みにします。
このプロジェクトは、ゲームとしてではなく、創作のための環境として使われることを想定しています。

## 対象バージョン

- Python 3.5.3
  - 2017-09-07-raspbian-stretch-lite.img
- 上記以降のバージョン

## 動作確認環境

- Python 3.6.1
  - macOS High Sierra 10.13
- Python 3.5.3
  - Raspbian stretch lite 2017-09-07

## 試行方法

まず、ソースコードを取得して、サーバーを起動します。

```
$ git clone https://github.com/nosix/PyMineHub.git
$ cd PyMineHub
PyMineHub $ bin/run.sh
In your environment, Python 3.6.1 is used.
INFO:pyminehub.config:RAKNET_SERVER_PORT=19132
INFO:pyminehub.config:TCP_SERVER_PORT=19142
INFO:pyminehub.config:WORLD_NAME=PyMineHub
INFO:pyminehub.config:GAME_MODE=SURVIVAL
INFO:pyminehub.config:SPAWN_MOB=True
INFO:pyminehub.config:INIT_SPACE=(32, 32)
INFO:pyminehub.config:PLAYER_SPAWN_POSITION=(256, 56, 256)
INFO:pyminehub.mcpe.plugin.loader:Plugin is loaded from directory "plugin".
INFO:pyminehub.mcpe.plugin.loader:AboutCommandProcessor was registered into CommandRegistry.
INFO:pyminehub.mcpe.plugin.loader:LevelDBChunkGeneratorPlugin overrode ChunkGeneratorPlugin.
INFO:pyminehub.mcpe.plugin.loader:ActionCommandProcessor was registered into CommandRegistry.
INFO:pyminehub.mcpe.plugin.loader:GameEventCommandProcessor was registered into CommandRegistry.
```

マインクラフトのフレンドタブから、ゲームを開始します。
PyMineHub はマインクラフトバージョン 1.2.7 (たぶん、それ以降も)、プロトコルバージョン 160 に対応しています。
マインクラフトバージョン 1.2.10 で動作を確認しています。

ゲームを開始すると、水だけの世界が生成されます。
さらに、鳥たちがでたらめに動きます。
もし、生成される世界やモブの動きを変えたい場合は、プラグインを使います。
基本設定では、カレントディレクトリにある `plugin` ディレクトリ配下にあるソースコードを読み込みます。
もし、プラグインを読み込むディレクトリを変更したい場合は、`MPH_PLUGIN_ROOT` 環境変数にディレクトリを指定します。
プラグインを無効にする場合は、`MPH_PLUGIN_ROOT` 環境変数に `""` を指定します。
`run.sh` コマンドでは `-d` オプションを付けて実行すると、プラグインを無効にできます。

```
PyMineHub $ rm PyMineHub-p0.db 
PyMineHub $ bin/run.sh -d
In your environment, Python 3.6.1 is used.
INFO:pyminehub.config:RAKNET_SERVER_PORT=19132
INFO:pyminehub.config:TCP_SERVER_PORT=19142
INFO:pyminehub.config:WORLD_NAME=PyMineHub
INFO:pyminehub.config:GAME_MODE=SURVIVAL
INFO:pyminehub.config:SPAWN_MOB=True
INFO:pyminehub.config:INIT_SPACE=(32, 32)
INFO:pyminehub.config:PLAYER_SPAWN_POSITION=(256, 56, 256)
INFO:pyminehub.mcpe.plugin.loader:PMH_PLUGIN_ROOT=
INFO:pyminehub.mcpe.plugin.loader:Plugin is disabled.
```

`PyMineHub-p0.db` はデータファイルです。
現在は SQLite DB を使用していますが、変更するかもしれません(時期は未定)。
もし、`INIT_SPACE` が指定されているならば、
サーバーを起動した時に指定した領域のチャンク(地形データの断片)が生成され、
この領域のチャンクが他の領域に複製されます。
もし、`INIT_SPACE` が `None` ならば、チャンクは必要に応じて生成されます。
これは、プレイ中の CPU 負荷を軽減するための機能です。

再び、マインクラフトのフレンドタブから、ゲームを開始します。
ゲームを開始すると、草だけの世界が生成されます。
さらに、鳥たちがでたらめに動きます。
この例では、プラグインディレクトリは読み込まれず、基本のプラグインが使われています。
基本のプラグインは `src/pyminehub/mcpe/plugin/default` にあります。
そして、プラグインのインターフェースは `src/pyminehub/mcpe/plugin` にあります。

- `ChunkGeneratorPlugin`
  - 上書き (override)
- `MobProcessorPlugin`
  - 上書き (override)
- `PlayerConfigPlugin`
  - 上書き (override)
- `ExtraCommandPlugin`
  - 追加

(最初の例の様に) `-d` オプションを付けずに `run.sh` コマンドを実行した時、
`plugin` ディレクトリの `LevelDBChunkGeneratorPlugin` は基本のプラグインを上書きします。
上書きの場合、最後に読み込まれたプラグインが有効になります。
一方、`ExtraCommandPlugin` は複数追加され、読み込まれた全てのプラグインが有効になります。

## プラグイン

### ExtraCommandPlugin (拡張コマンドプラグイン)

このプラグインはコマンドの使用を有効にします。
コマンドによって、サーバーを操作できます。
プラグインはコマンド処理器を返します。
クライアントがコマンドを実行した時、コマンド処理器のメソッドが実行されます。

例えば、`plugin/action/main.py` の `ActionCommandProcessor` は以下のとおりです。

```python
from binascii import unhexlify
from pickle import loads
from pyminehub.mcpe.command.annotation import String
from pyminehub.mcpe.command.api import CommandContext, command

class ActionCommandProcessor:

    @command
    def perform(self, context: CommandContext, args: str) -> None:
        """Perform action in the world."""
        self._perform(context, String(args))

    @perform.overload
    def _perform(self, context: CommandContext, data: String) -> None:
        action = loads(unhexlify(data))
        context.perform_action(action)
```

`ActionCommandProcessor` は `/perform data` コマンドを提供します。
コマンド名 `perform` はメソッド名 `perform` から名付けられます。
メソッドに `command` デコレータを適用すると、メソッド名がコマンド名になります。
メソッドの引数は `CommandContext` と `str` でなければなりません。

クライアントにメソッドのシグニチャを提供するために、`overload` デコレータを使います。
シグニチャはコマンドの使用方法を示すために使われます。
`overload` デコレータを付与されたメソッドの引数は、
`CommandContext` と `pyminehub.mcpe.command.annotation` で定義された型でなければなりません。
メソッドを呼ぶ時に、`pyminehub.mcpe.command.annotation` で定義された型に包むことで、オーバーロードが有効になります。
そのため、これらのメソッドの名前は同じで構いません。

## クライアント

サーバーだけではなく、簡易クライアントも提供しています。

例えば、`plugin/action/client.py` の `ActionCommandClient` は以下のとおりです。

```python
from binascii import hexlify
from pickle import dumps
from typing import Union
from pyminehub.mcpe.action import Action, ActionType, action_factory
from pyminehub.mcpe.network import MCPEClient
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.const import MoveMode
from pyminehub.mcpe.main.client import connect

class ActionCommandMixin:

    @property
    def client(self) -> MCPEClient:
        raise NotImplementedError()

    def perform_action(self, action_or_type: Union[Action, ActionType], *args, **kwargs) -> None:
        action = action_factory.create(action_or_type, *args, **kwargs) \
            if isinstance(action_or_type, ActionType) else action_or_type
        data = hexlify(dumps(action)).decode()
        self.client.execute_command('/perform {}'.format(data))

class ActionCommandClient(MCPEClient, ActionCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self

def run_client():
    with connect('127.0.0.1', player_name='Taro', client_factory=ActionCommandClient) as client:
        client.perform_action(
            ActionType.MOVE_PLAYER, 1, Vector3(256.0, 64.0, 256.0), 0.0, 0.0, 0.0, MoveMode.NORMAL, True, 0, True)
        client.wait_response(timeout=10)
        print(client.get_entity())
```

`connect` メソッドによってサーバーに接続します。
クライアントを拡張するためには、`client_factory` 引数を指定します。
`client_factory` 引数には、`MCPEClient` を継承したクラスのインスタンスを生成する関数を指定します。
サーバーへの接続に成功した時、
生成されたインスタンスは `as` で指定した `client` 変数に設定されます。

`wait_response` メソッドは、何らかのパケットを待ちます。
直前に送信したパケットの応答を待つのではありません。
何らかのパケットを受信したならば、次の処理に進みます。

`test/multiplay.py` も参照してください。

## サーバー設定

設定を変えたい場合には、`src/pyminehub/mcpe/main/server.py` を編集します。
例えば、`src/pyminehub/mcpe/main/server.py` の一部は以下のとおりです。

```python
if __name__ == '__main__':
    from pyminehub.config import set_config
    set_config(game_mode='CREATIVE', spawn_mob=False)
    set_config(
        world_name='Small',
        init_space=(1, 1),
        player_spawn_position=(0, 56, 0)
    )
    # ... snip ...
```

`set_config` は一つにまとめても、複数に分けても構いません。
引数名は `pyminehub.config` に定義されています。

- システム設定
  - ip_version : サーバーが対応する IP プロトコルのバージョン
    - デフォルト 4 ですが、たぶん 6 でも動きます (動かなかったら、ごめんなさい)
  - raknet_server_port : RakNet プロトコルで通信するポートの番号
    - デフォルトは 19132 (マインクラフトが使用している番号)
  - tcp_server_port : TCP プロトコルで通信するポートの番号
    - デフォルトは 19142 (適当に付けた番号)
  - max_log_length : ログの一行の最大文字数
    - None の場合は、全文字表示します
- RakNet 設定
  - server_guid : サーバーの ID (8 バイト整数)
    - None の場合は、ランダムで自動的に割り当てます
  - resend_time : パケットを再送する間隔 (ミリ秒)
- ワールド設定
  - seed : 地形のシード
    - 現在は、シードを指定しても地形は変わりません
  - difficulty : 難易度 (PEACEFUL, EASY, NORMAL, HARD)
    - 現在は、難易度による違いはありません
  - rain_level : 雨レベル (0.0 〜 1.0 だったはず)
    - 現在は、雨レベルによる違いはありません
  - lightning_level : 明かりレベル (0.0 〜 1.0 だったはず)
    - 現在は、明かりレベルによる違いはありません
  - world_tick_time : ワールドの更新間隔 (秒)
    - 厳密にこの間隔で更新されるわけではなく、大体です
  - spawn_mob : モブを生成するか？ (True, False)
    - デフォルトは True (生成する)
  - clock_time : 時計の時刻 (0 〜 19200)
    - None の場合は、時刻が変わり、全クライアントで同期します (デフォルト)
    - 正の整数の場合は、常に指定した時刻で全クライアントを同期します
    - 負の整数の場合は、指定した時刻で開始しますが、クライアント間で同期させません
  - clock_tick_time : 時刻を同期する間隔 (秒)
    - デフォルトは 10.0 (適当です)
  - init_space : サーバー起動時に初期化する地形データ領域のサイズ (整数, 整数)
    - デフォルトは (32, 32)
    - None の場合は、サーバー起動時に地形データを生成しません
      - プレイ中に生成するため、プレイ中に処理が遅くなる恐れがあります
    - 整数の組を指定した場合は、指定された領域の地形データを生成し、他の領域はその領域から複製します
      - 値が大きい程、初回起動が遅くなります
  - player_spawn_position : プレイヤーの出発地点 (東西, 高さ, 南北)
    - 東西、南北は、正と負の小数
    - 高さは、1 〜 128 の小数
- RakNet とワールドの共通設定
  - world_name : ワールド名称
    - デフォルトは PyMineHub
  - game_mode : ゲームモード (SURVIVAL, CREATIVE, ADVENTURE)
    - ADVENTURE には対応していません
- ネットワーク設定
  - batch_compress_threshold : パケットのデータを圧縮する下限
    - データサイズが指定した値以上の場合は、データを圧縮します
    - 圧縮を行うと CPU 負荷が上がり、ネットワーク負荷が下がります
  - rough_move : 移動の処理を雑にするか？ (True, False)
    - デフォルトは True
    - 雑にすると移動パケットを再送しません
    - 再送しない場合、パケットが紛失したときに移動後の停止位置がずれるかもしれません
    - 雑にすることでネットワーク負荷が大幅に減ります

### 参考

- このプロジェクトは [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) のソースコードを参照して実装されています。
- [RakNet](http://www.raknet.net/raknet/manual/systemoverview.html)
- [Pocket Edition Protocol Documentation](http://wiki.vg/Pocket_Edition_Protocol_Documentation)
- [Java Edition data values](https://minecraft.gamepedia.com/Java_Edition_data_values)