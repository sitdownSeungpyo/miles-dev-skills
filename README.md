# miles-dev-skills

로봇·임베디드·웹·앱 개발 작업에 특화된 개인용 Claude Code 스킬/플러그인 모음입니다.
전세계 개발자들이 가장 많이 쓰는 스킬·플러그인 상위 100개 리서치(→ [REFERENCES.md](REFERENCES.md))를
기반으로, 검증된 패턴만 추려 12개 스킬과 1개 서브에이전트로 작성했습니다.
멀티 에이전트 오케스트레이션은 [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)(OMC, MIT) 위에서 동작하며,
miles-dev-skills는 OMC가 모르는 **하드웨어 안전 규칙**과 도메인 스킬을 그 위에 얹습니다.

## 포함된 스킬

| 스킬 | 분야 | 트리거 상황 |
|---|---|---|
| `honest-reporting` | 공통(전 분야) | 모든 답변 — 확인/추정/모름 구분, 근거 없는 단정·무조건 동의 금지 |
| `ros2-dev` | 로보틱스 | ROS 2 노드/launch/QoS/Nav2/micro-ROS 작업 시 |
| `embedded-firmware` | 임베디드 | STM32/ESP32/nRF 펌웨어, ISR, RTOS, 드라이버 작성 시 |
| `platformio-arduino` | 임베디드 | platformio.ini, .ino, Arduino 프레임워크 프로토타이핑 시 |
| `hw-debug` | 하드웨어 | UART/I2C/SPI/CAN/BLE 통신 불량, SWD 디버깅 시 |
| `web-frontend` | 웹 | React/Next.js UI, 실시간 로봇 대시보드 개발 시 |
| `api-backend` | 웹/서버 | FastAPI/Node API, 텔레메트리 수집, 로봇 관제 백엔드 시 |
| `flutter-app` | 앱 | Flutter 앱, BLE/WiFi 로봇 컨트롤러 앱 개발 시 |
| `robot-deploy` | 배포 | Docker/ROS 배포, 펌웨어 CI, OTA 업데이트 설계 시 |
| `agent-orchestration` | 공통(워크플로) | 여러 파일·영역에 걸친 작업 — Fable이 OMC 워크플로·에이전트를 골라 위임하고, 하드웨어 안전 규칙 적용·검증 |
| `orchestration-monitor` | 모니터링 | "모니터 띄워줘" — 모델·서브에이전트 작업 현황과 토큰 사용량 GUI (cmux 분할창/브라우저) |
| `orchestration-setup` | 셋업 | 새 PC에서 miles + OMC 플러그인, OMC HUD, 기본 모델(Fable), 전역 CLAUDE.md를 한 번에 셋업 |

## 스킬별 사용 예제

각 스킬을 어떤 요청에서 쓰는지, 그때 Claude가 무엇을 하는지 정리했습니다.

### `honest-reporting`
> 예: "이 보드 UART 115200으로 맞아?" (설명 기반 자동 호출 — 상시 규칙은 전역 CLAUDE.md §0)

→ 사실 주장마다 **확인함 / 추정 / 모름**을 붙이고, 실행하지 않은 빌드·테스트는 "미검증"으로 씁니다.

### `ros2-dev`
> 예: "카메라 노드를 만들고 launch 파일에 넣어줘. 이미지 토픽은 센서용 QoS로."

→ `ROS_DISTRO`나 `package.xml`로 배포판을 먼저 확인하고, `ros2 pkg create`로 패키지를 만듭니다. 센서 스트림은 `SensorDataQoS`, launch 값은 `DeclareLaunchArgument`로 둡니다.

### `embedded-firmware`
> 예: "STM32에서 UART 수신을 DMA로 받고 ISR에서 링버퍼에 넣는 코드 짜줘."

→ MCU·클럭·RAM 가정을 먼저 밝히고, ISR은 플래그/큐 저장만 하며 공유 변수는 `volatile`로 선언합니다. 빌드는 호스트에서만 확인하고, 타이밍은 보드에서 로직 애널라이저로 측정해야 하므로 **보드 미검증**으로 보고합니다.

### `platformio-arduino`
> 예: "ESP32에서 센서값을 읽어 MQTT로 보내는 스케치 만들어줘. 환경 이름은 esp32dev."

→ `platformio.ini`에 `[env]` 공통 설정과 `[env:esp32dev]`를 두고, 라이브러리는 `@^x.y`로 고정합니다. `delay()` 대신 `millis()` 비차단 타이머를 쓰고, 빌드는 `pio run -e esp32dev`로 확인합니다. 업로드(`-t upload`)는 사용자 승인 후 메인 세션에서 합니다.

### `hw-debug`
> 예: "I2C 센서가 주소 스캔에 안 잡혀. 전원은 들어와 있어."

→ 전원 → 클럭 → 전기 → 프로토콜 → 로직 순서로 계층을 좁힙니다. 풀업 저항(2.2k–10k), SDA/SCL 교차 여부를 먼저 보고, 결과는 "증상 → 격리한 계층 → 근거 → 유력 원인 → 다음 테스트" 형식으로 씁니다.

### `web-frontend`
> 예: "관절 상태를 보여주는 Next.js 대시보드 만들어줘. 데이터는 WebSocket으로 받아."

→ 기존 `package.json` 스택을 먼저 따르고, 없으면 Next.js App Router + TypeScript strict + Tailwind를 씁니다. WebSocket 연결은 Provider 한 곳에 두고 지수 백오프 재연결과 연결 상태 표시를 넣으며, 고빈도 데이터는 10–15 Hz로 묶어 그립니다.

### `api-backend`
> 예: "로봇 이동 명령 API 만들어줘. 네트워크 재시도로 두 번 실행되면 안 돼."

→ FastAPI + Pydantic v2로 `/api/v1/...` 라우트를 만들고, 물리 동작 명령에는 idempotency key를 둡니다. 명령은 `pending → sent → acked → done/failed/timeout` 생명주기로 저장하며, 타임아웃과 재조정 경로를 포함합니다.

### `flutter-app`
> 예: "BLE로 로봇 컨트롤러에 연결하는 화면 만들어줘. 끊기면 자동 재연결해."

→ Riverpod provider로 연결 상태(scanning → connecting → discovering → ready → lost)를 노출하고, 백오프 재연결과 Android 12+ `BLUETOOTH_SCAN/CONNECT` 권한을 설정합니다. 화면은 `AsyncValue`의 loading/error/data 세 상태를 모두 처리합니다.

### `robot-deploy`
> 예: "ROS 2 노드를 Docker로 묶고 로봇 두 대에 단계적으로 배포하는 계획 짜줘."

→ `ros:<distro>-ros-base` 기반 멀티 스테이지 빌드와 필요한 장치만 매핑한 `docker compose` 구성을 제안합니다. 배포 순서는 bench → 카나리 로봇 1대 → 전체이며, 실제 배포는 사용자 승인 후 메인 세션에서 합니다.

### `agent-orchestration`
> 예: "모터 온도를 펌웨어에서 읽어 웹 대시보드에 표시해줘." (여러 영역에 걸친 작업 시 설명 기반 자동 호출)

→ `ralplan`으로 계획을 세우고 `/team`이나 `executor`(`model: opus`)에 구현을 맡깁니다. 펌웨어 변경은 `hw-safety-reviewer` 검토를 거친 뒤 보고하고, 플래시는 사용자 승인 후 메인 세션에서만 합니다.

### `orchestration-monitor`
> 예: "모니터 띄워줘"

→ 로컬 서버(`http://127.0.0.1:8765/`)를 띄우고 모델별 토큰 사용량과 서브에이전트 상태를 3초마다 갱신합니다. Claude가 스킬 디렉터리의 `monitor.py`를 `--launch`로 실행합니다(Windows에서는 `python3` 대신 `py -3`). 일회성 확인이면 `--dump`로 JSON만 출력할 수 있습니다.

### `orchestration-setup`
> 예: "SETUP.md 읽고 셋업해줘"

→ 각 단계를 먼저 확인하고 이미 된 단계는 건너뜁니다. `settings.json`과 `CLAUDE.md`는 수정 전에 `.bak-<날짜>`로 백업하고, 기본 모델을 `fable`로 맞춘 뒤 전역 CLAUDE.md에 miles 오버레이를 추가합니다. 적용은 새 Claude Code 세션부터입니다.

### `hw-safety-reviewer` (에이전트)
> 예: "방금 바꾼 모터 정지 ISR 코드 hw-safety-reviewer로 검토해줘."

→ 읽기 전용 Opus 에이전트가 `SAFE TO PROCEED / FIX BEFORE ON-TARGET TEST / BLOCK` 중 하나의 판정과 `path:line` 근거(CONFIRMED/PLAUSIBLE)를 냅니다. 보드에서만 확인할 수 있는 항목 목록도 함께 나오며, 수정하거나 장치에 명령을 보내지는 않습니다.

## 오케스트레이션 (Fable 지휘 + oh-my-claudecode)

메인 세션(기본값: `fable` 별칭 — 최신 Fable 릴리스)이 계획·모드 선택·검증·승인을 맡고, 실제 작업은 OMC 워크플로와 에이전트가 합니다.

- **기본 흐름:** `plan`/`ralplan` → `execute`(독립 작업이 여럿이면 `/team`) → `review` → `verify`. 요구사항이 모호하면 먼저 `deep-interview`.
- **OMC 에이전트(기본 모델):** `explore`·`writer`(Haiku), `executor`·`debugger`·`tracer`·`test-engineer`·`verifier`·`designer`(Sonnet), `architect`·`code-reviewer`·`security-reviewer`·`critic`·`planner`(Opus) 등 19종. 이 저장소 규칙에서는 `executor`·`debugger`를 `model: opus`로 호출합니다(작업 모델 = Opus).
- **miles 전용 에이전트:** `hw-safety-reviewer`(Opus, 읽기 전용). 펌웨어·드라이버·ISR·제어 루프·버스 프로토콜·E-stop·OTA 변경의 필수 관문입니다.
- **하드웨어 규칙:** 보드 플래시, 실제 장치 명령, OTA, 로봇 배포, push는 메인 세션에서 사용자 승인 후에만 합니다. OMC 워커나 루프(`team`/`autopilot`/`ralph`)는 하지 않습니다.

규칙 전체는 `skills/agent-orchestration/SKILL.md`에 있습니다. OMC 설명은 [OMC README](https://github.com/Yeachan-Heo/oh-my-claudecode)를 참고하세요.

### 모니터 GUI

Claude에게 **"모니터 띄워줘"**라고 하거나 직접 실행하세요 (Python 3 표준 라이브러리만 사용):

```bash
python3 skills/orchestration-monitor/monitor.py --launch
```

`http://127.0.0.1:8765/`에서 모델별 토큰 사용량, 세션별 모델 비율, 서브에이전트(OMC 에이전트 포함) 상태와 마지막 작업을 3초마다 갱신해 보여줍니다. cmux 안에서 실행하면 옆 분할창에 열립니다. 한 줄 요약은 OMC HUD(상태줄)에서 볼 수 있습니다.

### 새 PC 셋업

저장소를 clone한 뒤 그 폴더에서 `claude`를 실행하고 **"SETUP.md 읽고 셋업해줘"**라고 하면 됩니다.
자세한 절차는 [SETUP.md](SETUP.md)와 `skills/orchestration-setup/SKILL.md`를 참고하세요.

## 설치 방법

### 방법 1 — 개인 전역 스킬로 사용 (가장 간단)

스킬 폴더를 `~/.claude/skills/`에 복사하면 모든 프로젝트에서 자동 활성화됩니다:

```powershell
Copy-Item -Recurse C:\miles_skills\miles-dev-skills\skills\* $env:USERPROFILE\.claude\skills\
```

### 방법 2 — 로컬 마켓플레이스 플러그인으로 설치

Claude Code에서:

```
/plugin marketplace add C:\miles_skills\miles-dev-skills
/plugin install miles-dev-skills@miles-dev-skills
```

### 방법 3 — 특정 프로젝트에만 적용

프로젝트의 `.claude/skills/`에 필요한 스킬 폴더만 복사합니다.

## 구조

```
miles-dev-skills/
├── .claude-plugin/
│   ├── plugin.json          # 플러그인 매니페스트
│   └── marketplace.json     # 로컬 마켓플레이스 정의
├── agents/                  # hw-safety-reviewer (나머지 에이전트는 OMC가 제공)
├── skills/
│   └── <skill-name>/SKILL.md
├── SETUP.md                 # 새 PC 셋업 진입점 (Claude가 읽고 실행)
├── REFERENCES.md            # 전세계 인기 스킬/플러그인 TOP 100 리서치
└── README.md
```

## 스킬 추가/수정 방법

1. `skills/<새이름>/SKILL.md` 생성 — frontmatter의 `name`, `description`이 핵심입니다.
   `description`에 "언제 이 스킬을 쓰는지"를 구체적으로 적어야 Claude가 자동으로 불러옵니다.
2. `.claude-plugin/plugin.json`의 `skills` 배열에 경로 추가.
3. 본문은 간결하게: 규칙 위주(MUST DO / MUST NOT), 표와 체크리스트 활용.
   긴 참고자료는 스킬 폴더 안에 별도 `.md`로 두고 본문에서 링크하면
   필요할 때만 로드됩니다(progressive disclosure).

## 함께 쓰면 좋은 외부 플러그인 (리서치 상위권)

- **Context7** — React/Next.js 등 최신 라이브러리 문서 주입 (설치 34만+)
- **Superpowers** — 계획→스펙→테스트 워크플로 (설치 75만+)
- **Playwright Plugin** — 웹 대시보드 E2E 테스트
- **GitHub Plugin** — PR 리뷰/이슈 연동
- **ros2-engineering-skills** (dbwls99706) — 더 깊은 ROS 2 레퍼런스가 필요할 때

전체 순위는 [REFERENCES.md](REFERENCES.md) 참고.
