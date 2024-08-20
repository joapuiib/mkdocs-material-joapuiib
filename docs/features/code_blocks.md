---
title: Code blocks
---

## Code blocks
### Python block with line highlighting and line numbers
```python hl_lines="2" linenums="1"
def hello():
    print("Hello, world!")
```

Using the `hl_lines` attribute, you can highlight specific
lines in the code block.
````md
```python hl_lines="2" linenums="1"
...
```
````

### Javascript block
```javascript
function hello() {
    console.log("Hello, world!");
}
```

### Bash block
```bash
echo "Hello, world!"
```

### Shell block
```shellconsole
joapuiib@FP:~/git_tutorial (main) $ echo "Hello world!"
(venv) joapuiib@FP:~/git_tutorial (main) $ git diff
diff --git a/README.md b/README.md
index 6d747b3..ff524e4 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,4 @@
 # Tutorial de Git
 Estem aprenent a utilitzar Git!
+
+Hem modificat un fitxer existent.
-Hem eliminat un fitxer.
joapuiib@FP:~/git_tutorial (main) $ git push
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
To /home/joapuiib/gitflow_example/remot
   0fb88ef..9e34bb0  develop -> develop
joapuiib@FP:~/git_tutorial (main) $ git lga
* f853946 - (7 minutes ago) README: Afegits autors - Mar (origin/feature/author)
| * cc8c388 - (9 minutes ago) LICENSE: Afegida llicència - Pau (origin/feature/license)
|/  
| * 9e34bb0 - (15 minutes ago) README: Afegida descripció del projecte - Anna (HEAD -> develop, origin/develop, feature/readme, origin/feature/readme)
|/  
* 0fb88ef - (29 minutes ago) 1. Primer commit - Joan Puigcerver (origin/main, origin/HEAD, main)
[user@host ~ (main)] $ echo "Hello, world!"
(venv) [user@host ~] $ echo "Hello, world!"
```

#### Git output
```shellconsole
joapuiib@FP:~/git_tutorial (main) $ git status
joapuiib@fp:~/01_introduccio (main) $ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    README.md
	    modified:   mkdocs.yml
	    modified:   requirements.txt

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```


### Keyboard keys
++ctrl+alt+del++

```md
++ctrl+alt+del++
```
