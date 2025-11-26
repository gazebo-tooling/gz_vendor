async function deleteStaleBranches(delay=500) {     
    var branch_menu = document.getElementsByName("Branch menu");

    var stale_branch = [];
    for (const menu of branch_menu) {
      stale_branch.push(menu.parentElement.firstChild);
    }

    for (const branch of stale_branch) {
      branch.click();
      await new Promise(r => setTimeout(r, delay));     
    };
}  (() => { deleteStaleBranches(500); })();

