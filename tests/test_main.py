from dungeon_game import main


def test_main_runs(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello from dungeon-game!" in captured.out
