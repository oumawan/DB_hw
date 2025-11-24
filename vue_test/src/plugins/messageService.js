import { reactive } from 'vue'

// messages is a reactive array consumed by MessageHost
const state = reactive({ messages: [] })

let idCounter = 1

const MAX_TEXT_LENGTH = 1000

function _truncateText(text) {
  if (text === null || text === undefined) return ''
  const s = String(text)
  if (s.length <= MAX_TEXT_LENGTH) return s
  return s.slice(0, MAX_TEXT_LENGTH) + '...'
}

/**
 * show a message
 * opts:
 *  - type: 'info'|'success'|'error'|'warning'
 *  - duration: ms (<=0 = sticky)
 *  - background, color: custom styles
 *  - allowDuplicates: boolean (default false) — if false, identical messages (text+type) won't be added
 */
function show(text, opts = {}) {
  const id = idCounter++
  const truncated = _truncateText(text)
  const message = {
    id,
    text: truncated,
    type: opts.type || 'info',
    // preserve modal flag and other meta from opts
    modal: !!opts.modal,
    duration: typeof opts.duration === 'number' ? opts.duration : 3000,
    background: opts.background || '',
    color: opts.color || ''
  }
  // optional meta
  if (opts.priority) message.priority = opts.priority
  if (typeof opts.sticky !== 'undefined') message.sticky = !!opts.sticky

  const allowDup = !!opts.allowDuplicates

  // Deduplication: if not allowed, don't add identical (text+type) message when it's already visible
  if (!allowDup) {
    const existing = state.messages.find(m => m.text === truncated && m.type === message.type)
    if (existing) {
      // refresh its timer if duration provided
      if (message.duration > 0) {
        if (existing._timer) clearTimeout(existing._timer)
        existing._timer = setTimeout(() => close(existing.id), message.duration)
      }
      return existing.id
    }
  }

  // push and schedule removal
  state.messages.push(message)

  if (message.duration > 0) {
    message._timer = setTimeout(() => close(id), message.duration)
  }
  return id
}

function close(id) {
  const idx = state.messages.findIndex(m => m.id === id)
  if (idx !== -1) {
    const msg = state.messages[idx]
    if (msg._timer) clearTimeout(msg._timer)
    state.messages.splice(idx, 1)
  }
}

function clearAll() {
  state.messages.forEach(m => { if (m._timer) clearTimeout(m._timer) })
  state.messages.splice(0)
}

export default {
  state,
  show,
  close,
  clearAll,
  // convenience for showing a modal (centered, sticky by default)
  showModal(text, opts = {}) {
    // If a modal already exists, update its text and return its id
    const existing = state.messages.find(m => m.modal)
    if (existing) {
      existing.text = _truncateText(text)
      existing.background = opts.background || existing.background
      existing.color = opts.color || existing.color
      return existing.id
    }
    // ensure modal is sticky (duration 0) and mark modal flag
    const merged = Object.assign({}, opts, { modal: true, duration: 0, allowDuplicates: true })
    return show(text, merged)
  }
  ,
  /**
   * show a modal confirmation dialog. Returns a Promise<boolean> that resolves
   * to true if confirmed, false if cancelled.
   * opts: same as show, plus confirmText, cancelText
   */
  showConfirm(text, opts = {}) {
    const id = idCounter++
    const truncated = _truncateText(text)
    const message = {
      id,
      text: truncated,
      type: opts.type || 'info',
      modal: true,
      duration: 0, // sticky until user acts
      confirm: true,
      background: opts.background || '',
      color: opts.color || '',
      confirmText: opts.confirmText || '确认',
      cancelText: opts.cancelText || '取消'
    }

    // create a promise and attach resolve handler to message
    let resolver
    const promise = new Promise((resolve) => { resolver = resolve })
    // store resolver so MessageHost can call it when user acts
    message._resolve = (val) => { resolver(!!val) }

    state.messages.push(message)

    // return a promise that resolves to boolean and also closes the message when settled
    return promise.then((v) => {
      close(id)
      return v
    })
  }
}
