// A demo composition. Change a colour or a title here, then re-render just that beat from Beat Review.
window.DUR = 9;
window.SFX = [{ t: 0.1, role: 'pop', g: -10, why: 'the title lands' }, { t: 3, role: 'whoosh', g: -12, why: 'the scene changes' }, { t: 6, role: 'whoosh', g: -12, why: 'the scene changes' }];
window.SCENES = [
  { id: 'hook', from: 0, to: 3, layout: 'face', color: '#203a43', title: 'This is beat one' },
  { id: 'body', from: 3, to: 6, layout: 'gfx', color: '#7a3b12', title: 'Leave a note here' },
  { id: 'end', from: 6, to: 9, layout: 'split', color: '#2b2b66', title: 'Only this beat re-renders' },
];
