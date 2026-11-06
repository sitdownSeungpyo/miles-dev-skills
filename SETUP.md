# SETUP — 새 PC에서 오케스트레이션 환경 만들기

이 파일은 **Claude Code가 읽고 실행하는 셋업 진입점**입니다.

## 사람이 할 일 (1분)

```bash
git clone git@github.com:sitdownSeungpyo/miles-dev-skills.git ~/miles-dev-skills
cd ~/miles-dev-skills
claude
```

그리고 Claude Code에게:

> SETUP.md 읽고 셋업해줘

## Claude가 할 일

`skills/orchestration-setup/SKILL.md`를 읽고 그 절차를 0단계부터 순서대로 실행하세요. 요약:

1. Preflight: Claude Code, git 버전과 OS 확인
2. 이 저장소를 `$REPO`로 사용 (dirty가 아니면 `git pull --ff-only`)
3. 로컬 마켓플레이스 등록 → `miles-dev-skills@miles-dev-skills` 플러그인 설치 또는 업데이트 (스킬 + 서브에이전트 4종)
4. `~/.claude/settings.json`의 `"model"`을 `"fable"`로 변경 (백업 후 다른 키 보존, 사용자 확인)
5. `~/.claude/CLAUDE.md`에 `templates/global-CLAUDE.md` 블록 추가/갱신 (마커로 중복 방지)
6. 검증 결과를 붙여서 보고하고 새 세션을 열라고 안내

모든 단계는 멱등입니다. 이미 된 단계는 건너뛰고, 그렇다고 보고합니다.
