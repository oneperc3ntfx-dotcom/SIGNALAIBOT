kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📅 1 Bulan • Rp250.000",
                callback_data="pkg_1month"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 6 Bulan • Rp500.000",
                callback_data="pkg_6month"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 12 Bulan • Rp750.000",
                callback_data="pkg_12month"
            )
        ],
        [
            InlineKeyboardButton(
                text="👑 Permanent • Rp1.500.000",
                callback_data="pkg_permanent"
            )
        ]
    ]
)
