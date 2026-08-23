# miles-dev-skills

로봇·임베디드·웹·앱 개발 작업에 특화된 개인용 Claude Code 스킬/플러그인 모음입니다.
전세계 개발자들이 가장 많이 쓰는 스킬·플러그인 상위 100개 리서치(→ [REFERENCES.md](REFERENCES.md))를
기반으로, 검증된 패턴만 추려 9개 스킬로 작성했습니다.

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
├── skills/
│   └── <skill-name>/SKILL.md
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
